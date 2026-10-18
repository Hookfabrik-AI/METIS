"""MÉTIS pilot P2 (= P1 model with the slot-binding fix): small transformer over constraint/variable items.

P2 fix: each constraint slot (variable id + coefficient/sign + slot position) is embedded jointly by a small
MLP before the slots are summed, so coefficient-to-variable assignment, operand order (LT) and literal
polarity per variable (CLAUSE) are no longer lost.  P1 summed variables and coefficients separately.

Inputs per instance (A2 information boundary): domains, constraints, and - in repair modes - the
previous attempt and (mode FB only) the violation flags of that previous attempt.  Solutions,
solution counts and solver traces are never inputs.
Modes: 0 = fresh attempt, 1 = repair with flags (FB), 2 = repair with previous attempt but flags
masked (PREV / self-assessment input).
"""
from __future__ import annotations

import numpy as np
import torch
from torch import nn

import problems as P

MAXC, MAXV, NV = 24, 12, 16           # max constraints, max variables, value vocabulary
VAR_NONE, VAR_ALL = 16, 17
COEF_NONE = 7                         # coefficient vocab: -3..3 -> 0..6
CONST_OFF, CONST_N = 100, 256
MODE_FRESH, MODE_FB, MODE_PREV = 0, 1, 2


def encode_static(p: P.Problem) -> dict:
    """Static (attempt-independent) integer encoding of one problem."""
    assert len(p.constraints) <= MAXC and p.n <= MAXV
    ct = np.zeros(MAXC, np.int64); cv = np.full((MAXC, 4), VAR_NONE, np.int64)
    cc = np.full((MAXC, 4), COEF_NONE, np.int64); ck = np.zeros(MAXC, np.int64); ca = np.zeros(MAXC, np.int64)
    for i, c in enumerate(p.constraints):
        ct[i] = c.ctype
        if c.vars:
            cv[i, :len(c.vars)] = c.vars
        else:
            cv[i, 0] = VAR_ALL
        if c.ctype == P.CLAUSE:
            cc[i, :len(c.signs)] = [3 + (1 if s == 1 else -1) for s in c.signs]
        elif c.signs:
            cc[i, :len(c.signs)] = [3 + s for s in c.signs]
        ck[i] = min(max(c.const + CONST_OFF, 0), CONST_N - 1)
        ca[i] = c.aux
    lo = np.zeros(MAXV, np.int64); hi = np.zeros(MAXV, np.int64)
    for j, (a, b) in enumerate(p.domains):
        lo[j], hi[j] = a, b
    return {'ct': ct, 'cv': cv, 'cc': cc, 'ck': ck, 'ca': ca, 'nc': len(p.constraints), 'n': p.n, 'lo': lo, 'hi': hi}


def collate(statics: list, prev=None, flags=None, mode=MODE_FRESH) -> dict:
    """Batch tensors.  prev: list of attempts (or None); flags: list of bool arrays (only used for MODE_FB)."""
    B = len(statics)
    out = {k: torch.as_tensor(np.stack([s[k] for s in statics])) for k in ('ct', 'cv', 'cc', 'ck', 'ca', 'lo', 'hi')}
    nc = torch.as_tensor([s['nc'] for s in statics]); n = torch.as_tensor([s['n'] for s in statics])
    out['cmask'] = torch.arange(MAXC)[None] < nc[:, None]
    out['vmask'] = torch.arange(MAXV)[None] < n[:, None]
    pv = np.full((B, MAXV), NV, np.int64)               # NV = "no previous value"
    fl = np.zeros((B, MAXC), np.int64)                  # 0 = no flag info, 1 = satisfied, 2 = violated
    if prev is not None:
        for b, a in enumerate(prev):
            pv[b, :len(a)] = a
    if mode == MODE_FB and flags is not None:
        for b, f in enumerate(flags):
            fl[b, :len(f)] = np.where(f, 2, 1)
    out['prev'] = torch.as_tensor(pv); out['flag'] = torch.as_tensor(fl)
    out['mode'] = torch.full((B,), mode, dtype=torch.long)
    return out


class Net(nn.Module):
    def __init__(self, d=128, layers=4, heads=4, ff=256):
        super().__init__()
        self.d = d
        self.e_kind = nn.Embedding(3, d)               # cls / constraint / variable
        self.e_ctype = nn.Embedding(16, d)
        self.e_var = nn.Embedding(18, d)              # shared variable-id table (constraints + variables)
        self.e_slot = nn.Embedding(4, d)
        self.e_coef = nn.Embedding(8, d)
        self.e_const = nn.Embedding(CONST_N, d)
        self.e_aux = nn.Embedding(16, d)
        self.e_flag = nn.Embedding(3, d)
        self.e_lo = nn.Embedding(NV, d); self.e_hi = nn.Embedding(NV, d)
        self.e_prev = nn.Embedding(NV + 1, d)
        self.e_mode = nn.Embedding(3, d)
        self.bind = nn.Sequential(nn.Linear(d, d), nn.GELU(), nn.Linear(d, d))   # P2: joint slot binding
        layer = nn.TransformerEncoderLayer(d, heads, ff, dropout=0.0, batch_first=True, norm_first=True)
        self.enc = nn.TransformerEncoder(layer, layers, enable_nested_tensor=False)
        self.norm = nn.LayerNorm(d)
        self.out = nn.Linear(d, NV)
        # stage C heads (trained with frozen trunk): self-assessment p, strategy success q_rep / q_new
        self.head_p = nn.Sequential(nn.Linear(2 * d, d), nn.GELU(), nn.Linear(d, 1))
        self.head_q = nn.Sequential(nn.Linear(2 * d, d), nn.GELU(), nn.Linear(d, 2))

    def trunk(self, b: dict):
        B = b['ct'].shape[0]
        slot = self.e_slot.weight[None, None]                                   # 1,1,4,d
        used = ((b['cv'] != VAR_NONE) | (b['cc'] != COEF_NONE)).float()[..., None]
        cvar = (self.bind(self.e_var(b['cv']) + self.e_coef(b['cc']) + slot) * used).sum(2)
        cons = (self.e_kind.weight[1] + self.e_ctype(b['ct']) + cvar + self.e_const(b['ck'])
                + self.e_aux(b['ca']) + self.e_flag(b['flag']))
        vid = torch.arange(MAXV).expand(B, MAXV)
        var = (self.e_kind.weight[2] + self.e_var(vid) + self.e_lo(b['lo']) + self.e_hi(b['hi'])
               + self.e_prev(b['prev']))
        cls = (self.e_kind.weight[0] + self.e_mode(b['mode']))[:, None]
        x = torch.cat([cls, cons, var], 1)
        pad = ~torch.cat([torch.ones(B, 1, dtype=torch.bool), b['cmask'], b['vmask']], 1)
        h = self.norm(self.enc(x, src_key_padding_mask=pad))
        return h[:, 0], h[:, 1 + MAXC:]

    def logits(self, b: dict):
        cls, vh = self.trunk(b)
        lg = self.out(vh)                                                       # B, MAXV, NV
        vals = torch.arange(NV)[None, None]
        dom = (vals >= b['lo'][..., None]) & (vals <= b['hi'][..., None])
        return lg.masked_fill(~dom, -1e9), cls, vh

    def heads(self, b: dict):
        cls, vh = self.trunk(b)
        m = b['vmask'].float()[..., None]
        pooled = (vh * m).sum(1) / m.sum(1).clamp(min=1)
        z = torch.cat([cls, pooled], 1)
        return self.head_p(z)[:, 0], self.head_q(z)


def weights_sha256(net: nn.Module) -> str:
    import hashlib
    h = hashlib.sha256()
    for k, v in sorted(net.state_dict().items()):
        h.update(k.encode()); h.update(v.detach().cpu().numpy().tobytes())
    return h.hexdigest()
