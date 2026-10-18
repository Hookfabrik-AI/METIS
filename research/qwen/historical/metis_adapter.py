"""Smallest experimental adapter MÉTIS P2 -> text hints for an LLM (no service, no bundled integration).

Uses the existing trained checkpoint unchanged (METIS_P2/runs_p2/seed0/C/best.pt = B trunk + stage-C heads)
and the existing functions model.encode_static / model.collate / Net.logits / Net.heads.  Nothing is trained.
  propose(p)               -> greedy candidate, per-variable top-2 values with probabilities, p_hat (self-estimate)
  repair(p, prev, flags)   -> greedy candidate in FB mode (previous attempt + verifier flags as input)
render(p) turns a Problem into a plain mathematical task text (identical for both experiment arms).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

METIS = Path('<LOCAL_METIS_P2>')
sys.path.insert(0, str(METIS))

import torch  # noqa: E402

import model as M  # noqa: E402
import problems as P  # noqa: E402

CKPT = METIS / 'runs_p2' / 'seed0' / 'C' / 'best.pt'
PRED = {P.PRED_EVEN: 'gerade', P.PRED_ODD: 'ungerade', P.PRED_PRIME: 'Primzahlen'}


class Metis:
    def __init__(self, ckpt=CKPT, threads=4):
        torch.set_num_threads(threads)
        self.net = M.Net()
        self.net.load_state_dict(torch.load(ckpt, weights_only=True))
        self.net.eval()
        self.sha256 = M.weights_sha256(self.net)
        self.cpu_s = 0.0                       # accumulated process CPU time of all MÉTIS calls

    @torch.no_grad()
    def propose(self, p):
        c0 = time.process_time()
        st = [M.encode_static(p)]
        lg, _, _ = self.net.logits(M.collate(st))
        pr = torch.softmax(lg[0, :p.n], -1)
        top = torch.topk(pr, 2, -1)
        cand = [int(v) for v in lg[0, :p.n].argmax(-1)]
        hint = [[(int(top.indices[i, k]), float(top.values[i, k])) for k in range(2)] for i in range(p.n)]
        ph, _ = self.net.heads(M.collate(st, [cand], None, M.MODE_PREV))
        out = {'candidate': cand, 'top2': hint, 'p_hat': float(torch.sigmoid(ph[0]))}
        self.cpu_s += time.process_time() - c0
        return out

    @torch.no_grad()
    def repair(self, p, prev, flags):
        c0 = time.process_time()
        lg, _, _ = self.net.logits(M.collate([M.encode_static(p)], [list(prev)], [flags], M.MODE_FB))
        cand = [int(v) for v in lg[0, :p.n].argmax(-1)]
        self.cpu_s += time.process_time() - c0
        return {'candidate': cand}


def _term(coef, v):
    if coef == 1:
        return f'x{v}'
    if coef == -1:
        return f'-x{v}'
    return f'{coef}*x{v}'


def render_constraint(c, n):
    t, vs = c.ctype, list(c.vars) if c.vars else list(range(n))
    xs = ', '.join(f'x{v}' for v in vs)
    if t == P.NEQ:
        return f'x{vs[0]} != x{vs[1]}'
    if t == P.LT:
        return f'x{vs[0]} < x{vs[1]}'
    if t == P.EQC:
        return f'x{vs[0]} = {c.const}'
    if t == P.NEQC:
        return f'x{vs[0]} != {c.const}'
    if t in (P.SUM_EQ, P.SUM_LE, P.SUM_GE):
        op = {P.SUM_EQ: '=', P.SUM_LE: '<=', P.SUM_GE: '>='}[t]
        return f"{' + '.join(f'x{v}' for v in vs)} {op} {c.const}"
    if t in (P.CNT_GE, P.CNT_LE):
        op = 'mindestens' if t == P.CNT_GE else 'höchstens'
        return f'Unter {xs} sind {op} {c.const} {PRED[c.aux]} Werte'
    if t == P.NODIV:
        return f'Kein Wert unter {xs} teilt einen anderen, verschiedenen Wert davon ohne Rest'
    if t == P.GAP_GE:
        return f'|x{vs[0]} - x{vs[1]}| >= {c.const}'
    if t == P.CAP:
        return f'Höchstens {c.aux} der Variablen {xs} haben den Wert {c.const}'
    if t == P.CLAUSE:
        lits = [f'x{v} = 1' if s == 1 else f'x{v} = 0' for v, s in zip(vs, c.signs)]
        return ' ODER '.join(lits)
    if t == P.LIN_EQ:
        s = ' + '.join(_term(a, v) for a, v in zip(c.signs, vs)).replace('+ -', '- ')
        return f'{s} = {c.const}'
    raise ValueError(t)


def render(p):
    doms = '; '.join(f'x{i} ∈ {{{lo}, …, {hi}}}' for i, (lo, hi) in enumerate(p.domains))
    cons = '\n'.join(f'B{k + 1}: {render_constraint(c, p.n)}' for k, c in enumerate(p.constraints))
    return (f'Finde ganze Zahlen x0 bis x{p.n - 1}, die ALLE folgenden Bedingungen erfüllen.\n'
            f'Wertebereiche: {doms}\n'
            f'Bedingungen:\n{cons}')
