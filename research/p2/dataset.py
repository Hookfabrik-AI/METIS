"""Build the versioned P2 (MÉTIS) dataset - same generator and separation rules as P1, NEW seeds: seed-separated splits, cross-split dedup, manifest with hashes.
usage: python -I -B dataset.py OUT_DIR
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # -I drops the script dir from sys.path

import numpy as np

import problems as P

TRAIN_CLASSES = ('K1_numbers', 'K2_schedule', 'K3_logic', 'K4_equations')
SPLITS = [  # name, seed, classes, per-class count, hard ('alt' = alternative construction)
    ('train', 1101, TRAIN_CLASSES, 20000, False),
    ('test_alt', 7107, TRAIN_CLASSES, 500, 'alt'),
    ('dev', 2102, TRAIN_CLASSES, 500, False),
    ('test', 3103, TRAIN_CLASSES, 1000, False),
    ('test_hard', 4104, TRAIN_CLASSES, 500, True),
    ('test_k5', 5105, ('K5_coloring',), 1000, False),
    ('test_k5_hard', 6106, ('K5_coloring',), 500, True),
]
ORDER = ['test', 'test_hard', 'test_alt', 'test_k5', 'test_k5_hard', 'dev', 'train']   # evaluation sets claim first


def to_json(p: P.Problem, sols: np.ndarray) -> dict:
    return {'cls': p.cls, 'n': p.n, 'domains': p.domains,
            'constraints': [dataclasses.astuple(c) for c in p.constraints],
            'solutions': sols.tolist(), 'canonical': p.canonical(),
            'coarse': P.coarse_signature(p, len(sols))}


def from_json(d: dict):
    cons = [P.Constraint(t, tuple(v), tuple(s), c, a) for t, v, s, c, a in d['constraints']]
    return P.Problem(d['cls'], d['n'], [tuple(x) for x in d['domains']], cons), np.array(d['solutions'])


def build(out: Path):
    out.mkdir(parents=True, exist_ok=False)
    spec = {s[0]: s for s in SPLITS}
    taken: set[str] = set()
    coarse_taken: set[str] = set()
    eval_coarse: set[str] = set()
    manifest = {'format': 'METIS_P2_DATASET_V1', 'max_solutions': P.MAX_SOLUTIONS,
                'problems_sha256': hashlib.sha256(Path(P.__file__).read_bytes()).hexdigest(), 'splits': {}}
    for name in ORDER:
        _, seed, classes, count, hard = spec[name]
        rng = np.random.default_rng(seed)
        rows, dup, cdup = [], 0, 0
        for cls in classes:
            got = 0
            while got < count:
                p, sols = P.generate_alt(cls, rng) if hard == 'alt' else P.generate(cls, rng, bool(hard))
                p, sols = P.relabel(p, sols, rng)
                key, ckey = p.canonical(), P.coarse_signature(p, len(sols))
                if key in taken:
                    dup += 1
                    continue
                if ckey in coarse_taken and name != 'train' or (name == 'train' and ckey in eval_coarse):
                    cdup += 1          # possibly equivalent under renaming to an instance of an earlier split
                    continue
                taken.add(key)
                rows.append(to_json(p, sols)); got += 1
        if name != 'train':
            eval_coarse |= {r['coarse'] for r in rows}
        coarse_taken |= {r['coarse'] for r in rows}
        f = out / f'{name}.jsonl'
        f.write_text(''.join(json.dumps(r, separators=(',', ':')) + '\n' for r in rows))
        manifest['splits'][name] = {'seed': seed, 'classes': list(classes), 'per_class': count, 'hard': hard,
                                    'rows': len(rows), 'cross_split_duplicates_skipped': dup,
                                    'coarse_signature_collisions_skipped': cdup,
                                    'sha256': hashlib.sha256(f.read_bytes()).hexdigest()}
        print(name, len(rows), 'dup skipped', dup, flush=True)
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=1))


def load(path: Path):
    return [from_json(json.loads(line)) for line in Path(path).read_text().splitlines()]


if __name__ == '__main__':
    build(Path(sys.argv[1]))
