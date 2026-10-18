"""Decoding, verification and the pre-registered protocols (Nachtrag R1, A3/A4) shared by training and evaluation."""
from __future__ import annotations

import numpy as np
import torch

import model as M
import problems as P


@torch.no_grad()
def decode(net, statics, mode=M.MODE_FRESH, prev=None, flags=None, sample=False, gen=None, tau=1.0):
    lg, _, _ = net.logits(M.collate(statics, prev, flags, mode))
    if sample:
        pr = torch.softmax(lg / tau, -1)
        B, V, K = pr.shape
        x = torch.multinomial(pr.reshape(B * V, K), 1, generator=gen).reshape(B, V)
    else:
        x = lg.argmax(-1)
    x = x.numpy()
    return [x[b, :s['n']].copy() for b, s in enumerate(statics)]


@torch.no_grad()
def confidence(net, statics):
    """Untrained-head heuristic for the D1 rule: mean max-softmax of the fresh greedy attempt."""
    lg, _, _ = net.logits(M.collate(statics))
    pm = torch.softmax(lg, -1).max(-1).values
    vm = M.collate(statics)['vmask'].float()
    return ((pm * vm).sum(1) / vm.sum(1)).numpy()


def verify(problems, attempts):
    """Objective verifier: flags (True = violated) and correctness per attempt."""
    fl = [P.violations(p, a) for p, a in zip(problems, attempts)]
    ok = [bool(P.in_domain(p, a)) and not f.any() for p, a, f in zip(problems, attempts, fl)]
    return fl, np.array(ok)


def chunks(n, size=512):
    for i in range(0, n, size):
        yield slice(i, min(n, i + size))


def success_at_k(net, problems, statics, protocol, k=4, seed=0):
    """A3 protocol.  Round 1: greedy fresh attempt.  Rounds 2..k: tau=1 samples with identical seeds.
    FB: repair with previous attempt + its flags; PREV: repair with previous attempt, flags masked;
    NOFB: independent fresh samples.  Every candidate is verified (k verifier calls).
    Returns (success bool array, violations of last candidate)."""
    succ = np.zeros(len(problems), bool); last_v = np.zeros(len(problems), int)
    for sl in chunks(len(problems)):
        ps, ss = problems[sl], statics[sl]
        gen = torch.Generator().manual_seed(seed * 1000003 + sl.start)
        a = decode(net, ss)
        fl, ok = verify(ps, a)
        s = ok.copy()
        for _ in range(k - 1):
            if protocol == 'NOFB':
                a = decode(net, ss, sample=True, gen=gen)
            else:
                mode = M.MODE_FB if protocol == 'FB' else M.MODE_PREV
                a = decode(net, ss, mode, prev=a, flags=fl, sample=True, gen=gen)
            fl, ok = verify(ps, a)
            s |= ok
        succ[sl] = s
        last_v[sl] = [int(f.sum()) for f in fl]
    return succ, last_v


def strategy_rollout(net, problems, statics, a1, fl1, strategy, rounds=3, seed=0):
    """A4: run one fixed strategy loop from the state after a failed check of a1.
    'rep' = repair with flags each round, 'new' = fresh tau=1 sample each round. Stops at first success.
    Returns (solved bool, checks used)."""
    n = len(problems)
    solved = np.zeros(n, bool); used = np.zeros(n, int)
    for sl in chunks(n):
        gen = torch.Generator().manual_seed(seed * 7919 + sl.start + (0 if strategy == 'rep' else 500000))
        ps, ss = problems[sl], statics[sl]
        a, fl = a1[sl], fl1[sl]
        done = np.zeros(len(ps), bool); u = np.zeros(len(ps), int)
        for _ in range(rounds):
            if strategy == 'rep':
                a = decode(net, ss, M.MODE_FB, prev=a, flags=fl, sample=True, gen=gen)
            else:
                a = decode(net, ss, sample=True, gen=gen)
            fl, ok = verify(ps, a)
            u += ~done
            done |= ok
        solved[sl] = done; used[sl] = u
    return solved, used
