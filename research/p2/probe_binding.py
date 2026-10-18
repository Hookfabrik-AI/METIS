"""Counter-probes for the P2 slot-binding fix (P2 protocol section 1).
Pairs of problems that differ ONLY in coefficient-to-variable assignment, operand direction or literal
polarity.  For each pair: are the solution sets different (semantics)?  Does a model give the two problems
different internal representations (trunk outputs) and different output logits?
usage: python -I -B probe_binding.py P1_DIR P1_CKPT [P2_CKPT] OUT_JSON
  P1 model is loaded from its own (archived, unchanged) model.py; P2 untrained net uses seed 0.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import torch

import model as M2
import problems as P

C = P.Constraint


def pairs():
    d6 = [(0, 5)] * 3; d2 = [(0, 1)] * 3
    return {
        'LIN_EQ coefficient swap: x0+2x1=6 vs 2x0+x1=6':
            (P.Problem('K4_equations', 3, d6, [C(P.LIN_EQ, (0, 1), (1, 2), 6)]),
             P.Problem('K4_equations', 3, d6, [C(P.LIN_EQ, (0, 1), (2, 1), 6)])),
        'LIN_EQ 3 vars: x0-2x1+3x2=4 vs 3x0-2x1+x2=4':
            (P.Problem('K4_equations', 3, d6, [C(P.LIN_EQ, (0, 1, 2), (1, -2, 3), 4)]),
             P.Problem('K4_equations', 3, d6, [C(P.LIN_EQ, (0, 1, 2), (3, -2, 1), 4)])),
        'LT direction: x0<x1 vs x1<x0':
            (P.Problem('K2_schedule', 3, d6, [C(P.LT, (0, 1))]),
             P.Problem('K2_schedule', 3, d6, [C(P.LT, (1, 0))])),
        'CLAUSE polarity: (x0 or not x1) vs (not x0 or x1)':
            (P.Problem('K3_logic', 3, d2, [C(P.CLAUSE, (0, 1), (1, 0))]),
             P.Problem('K3_logic', 3, d2, [C(P.CLAUSE, (0, 1), (0, 1))])),
        'CLAUSE 3 literals: (x0 or not x1 or not x2) vs (not x0 or not x1 or x2)':
            (P.Problem('K3_logic', 3, d2, [C(P.CLAUSE, (0, 1, 2), (1, 0, 0))]),
             P.Problem('K3_logic', 3, d2, [C(P.CLAUSE, (0, 1, 2), (0, 0, 1))])),
    }


@torch.no_grad()
def reps(Mmod, net, p):
    b = Mmod.collate([Mmod.encode_static(p)])
    lg, cls, vh = net.logits(b)
    n = p.n
    return cls[0].numpy(), vh[0, :n].numpy(), lg[0, :n].numpy(), lg[0, :n].argmax(-1).numpy()


def compare(Mmod, net, a, b):
    ca, va, la, ga = reps(Mmod, net, a); cb, vb, lb, gb = reps(Mmod, net, b)
    fin = lambda x: x[x > -1e8]                            # ignore domain-masked logits
    return {'trunk_rel_diff': float(np.linalg.norm(np.r_[ca, va.ravel()] - np.r_[cb, vb.ravel()])
                                    / np.linalg.norm(np.r_[ca, va.ravel()])),
            'logit_max_abs_diff': float(np.abs(fin(la) - fin(lb)).max()),
            'greedy_a': ga.tolist(), 'greedy_b': gb.tolist(),
            'greedy_a_ok': bool(not P.violations(a, ga).any()), 'greedy_b_ok': bool(not P.violations(b, gb).any())}


def main():
    p1dir, p1ckpt = Path(sys.argv[1]), sys.argv[2]
    p2ckpt = sys.argv[3] if len(sys.argv) == 5 else None
    out = Path(sys.argv[-1])
    torch.set_num_threads(4)
    spec = importlib.util.spec_from_file_location('model_p1', p1dir / 'model.py')
    M1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(M1)
    net1 = M1.Net(); net1.load_state_dict(torch.load(p1ckpt, weights_only=True)); net1.eval()
    torch.manual_seed(0); net2u = M2.Net().eval()
    models = {'P1_trained': (M1, net1), 'P2_untrained': (M2, net2u)}
    if p2ckpt:
        net2 = M2.Net(); net2.load_state_dict(torch.load(p2ckpt, weights_only=True)); models['P2_trained'] = (M2, net2.eval())
    R = {'p1_ckpt': p1ckpt, 'p2_ckpt': p2ckpt, 'pairs': {}}
    for name, (a, b) in pairs().items():
        sa, sb = P.solve_all(a), P.solve_all(b)
        r = {'solutions_a': len(sa), 'solutions_b': len(sb),
             'solution_sets_differ': {tuple(x) for x in sa.tolist()} != {tuple(x) for x in sb.tolist()}}
        for k, (Mmod, net) in models.items():
            r[k] = compare(Mmod, net, a, b)
        R['pairs'][name] = r
        print(name, json.dumps({k: (v['trunk_rel_diff'], v['logit_max_abs_diff']) if isinstance(v, dict) else v
                                for k, v in r.items()}), flush=True)
    out.write_text(json.dumps(R, indent=1))


if __name__ == '__main__':
    main()
