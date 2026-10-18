"""Controlled, verifiable constraint problem classes (historical P2 implementation).

Every problem is n integer variables with per-variable domains inside 0..15 and a list of
constraints from one shared vocabulary.  `violations` is the objective verifier (one flag per
constraint).  `solve_all` enumerates every solution exactly (numpy); solutions are used only for
training targets and evaluation and are never part of a model input.

Instances are built around a planted assignment (guaranteed solvable).  Constraints are added
until at most MAX_SOLUTIONS assignments remain, then shuffled, so neither the constraint order
nor any single constraint identifies the planted assignment.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np

VMAX = 16                     # value vocabulary 0..15
MAX_SOLUTIONS = 32
PRIMES = {2, 3, 5, 7, 11, 13}

# constraint types (shared vocabulary)
NEQ, LT, EQC, NEQC, SUM_EQ, SUM_LE, SUM_GE, CNT_GE, CNT_LE, NODIV, GAP_GE, CAP, CLAUSE, LIN_EQ = range(1, 15)
TYPE_NAMES = {NEQ: 'NEQ', LT: 'LT', EQC: 'EQC', NEQC: 'NEQC', SUM_EQ: 'SUM_EQ', SUM_LE: 'SUM_LE',
              SUM_GE: 'SUM_GE', CNT_GE: 'CNT_GE', CNT_LE: 'CNT_LE', NODIV: 'NODIV', GAP_GE: 'GAP_GE',
              CAP: 'CAP', CLAUSE: 'CLAUSE', LIN_EQ: 'LIN_EQ'}
PRED_EVEN, PRED_ODD, PRED_PRIME = 1, 2, 3
CLASSES = ('K1_numbers', 'K2_schedule', 'K3_logic', 'K4_equations', 'K5_coloring')


@dataclass
class Constraint:
    ctype: int
    vars: tuple = ()          # variable indices (empty = all variables)
    signs: tuple = ()         # CLAUSE literal signs (1 = positive) / LIN_EQ coefficients
    const: int = 0            # constant (sum target, count, slot, gap ...)
    aux: int = 0              # predicate id (CNT_*), capacity (CAP)

    def key(self):
        return (self.ctype, self.vars, self.signs, self.const, self.aux)


@dataclass
class Problem:
    cls: str
    n: int
    domains: list             # list of (lo, hi) inclusive per variable
    constraints: list = field(default_factory=list)

    def canonical(self) -> str:
        cons = sorted(c.key() for c in self.constraints)
        return hashlib.sha256(json.dumps([self.cls, self.n, self.domains, cons]).encode()).hexdigest()


def _pred(values: np.ndarray, pred: int) -> np.ndarray:
    if pred == PRED_EVEN:
        return values % 2 == 0
    if pred == PRED_ODD:
        return values % 2 == 1
    return np.isin(values, list(PRIMES))


def eval_constraint(c: Constraint, X: np.ndarray) -> np.ndarray:
    """X: (m, n) int array of assignments -> (m,) bool, True = satisfied."""
    V = X[:, list(c.vars)] if c.vars else X
    t = c.ctype
    if t == NEQ:
        return V[:, 0] != V[:, 1]
    if t == LT:
        return V[:, 0] < V[:, 1]
    if t == EQC:
        return V[:, 0] == c.const
    if t == NEQC:
        return V[:, 0] != c.const
    if t == SUM_EQ:
        return V.sum(1) == c.const
    if t == SUM_LE:
        return V.sum(1) <= c.const
    if t == SUM_GE:
        return V.sum(1) >= c.const
    if t == CNT_GE:
        return _pred(V, c.aux).sum(1) >= c.const
    if t == CNT_LE:
        return _pred(V, c.aux).sum(1) <= c.const
    if t == NODIV:                       # no variable divides another (values >= 1)
        ok = np.ones(len(V), bool)
        for i, j in itertools.permutations(range(V.shape[1]), 2):
            a, b = V[:, i], V[:, j]
            ok &= ~((a > 0) & (b % np.maximum(a, 1) == 0) & (a != b))
        return ok
    if t == GAP_GE:
        return np.abs(V[:, 0] - V[:, 1]) >= c.const
    if t == CAP:                         # at most aux variables take value const
        return (V == c.const).sum(1) <= c.aux
    if t == CLAUSE:
        lit = [(V[:, i] == 1) if s == 1 else (V[:, i] == 0) for i, s in enumerate(c.signs)]
        return np.logical_or.reduce(lit)
    if t == LIN_EQ:
        return (V * np.array(c.signs)).sum(1) == c.const
    raise ValueError(t)


def violations(p: Problem, x) -> np.ndarray:
    """Objective verifier for one assignment: bool per constraint, True = VIOLATED.
    Out-of-domain values count as violating every constraint that mentions the variable."""
    X = np.asarray(x, dtype=np.int64).reshape(1, -1)
    out = np.array([not eval_constraint(c, X)[0] for c in p.constraints])
    bad = [i for i, (lo, hi) in enumerate(p.domains) if not lo <= X[0, i] <= hi]
    if bad:
        for k, c in enumerate(p.constraints):
            if not c.vars or set(c.vars) & set(bad):
                out[k] = True
    return out


def in_domain(p: Problem, x) -> bool:
    return all(lo <= v <= hi for v, (lo, hi) in zip(x, p.domains))


@lru_cache(maxsize=64)
def _space(doms: tuple) -> np.ndarray:
    grids = [np.arange(lo, hi + 1) for lo, hi in doms]
    return np.array(np.meshgrid(*grids, indexing='ij')).reshape(len(doms), -1).T.astype(np.int64)


@lru_cache(maxsize=16)
def _ascending(lo: int, hi: int, k: int) -> np.ndarray:
    return np.array(list(itertools.combinations(range(lo, hi + 1), k)), dtype=np.int64)


def solve_all(p: Problem, cap: int | None = None) -> np.ndarray:
    if p.cls == 'K1_numbers':
        # Exact: K1 always contains the strict chain x0 < x1 < ... (checked), so every solution is an
        # ascending combination; enumerating only those avoids a 15^k product space.
        chain = {(i, i + 1) for i in range(p.n - 1)}
        assert chain <= {c.vars for c in p.constraints if c.ctype == LT}, 'K1 without ascending chain'
        lo, hi = p.domains[0]
        X = _ascending(lo, hi, p.n)
    else:
        X = _space(tuple(map(tuple, p.domains)))
    ok = np.ones(len(X), bool)
    for c in p.constraints:
        idx = np.nonzero(ok)[0]
        if len(idx) == 0:
            break
        ok[idx] = eval_constraint(c, X[idx])
    S = X[ok]
    return S if cap is None else S[:cap]


# ---------------------------------------------------------------- generators
def _gen_numbers(rng, hard):
    k = int(rng.integers(5, 7)) if hard else int(rng.integers(4, 6))
    lo, hi = 1, 15
    plant = np.sort(rng.choice(np.arange(lo, hi + 1), size=k, replace=False))
    doms = [(lo, hi)] * k
    base = [Constraint(LT, (i, i + 1)) for i in range(k - 1)]   # ascending, distinct
    def cands():
        out = [Constraint(SUM_EQ, (), (), int(plant.sum()))]
        for pr in (PRED_EVEN, PRED_ODD, PRED_PRIME):
            cnt = int(_pred(plant, pr).sum())
            out.append(Constraint(CNT_GE, (), (), cnt, pr))
            out.append(Constraint(CNT_LE, (), (), cnt, pr))
        X = plant.reshape(1, -1)
        if eval_constraint(Constraint(NODIV), X)[0]:
            out.append(Constraint(NODIV))
        for _ in range(4):
            i, j = sorted(rng.choice(k, 2, replace=False))
            g = int(plant[j] - plant[i])
            if g >= 2:
                out.append(Constraint(GAP_GE, (int(i), int(j)), (), int(rng.integers(2, g + 1))))
            i = int(rng.integers(k)); v = int(rng.integers(lo, hi + 1))
            if v != plant[i]:
                out.append(Constraint(NEQC, (i,), (), v))
            sub = tuple(sorted(int(a) for a in rng.choice(k, int(rng.integers(2, 4)), replace=False)))
            s = int(plant[list(sub)].sum())
            out.append(Constraint(SUM_LE if rng.random() < .5 else SUM_GE, sub, (), s))
        return out
    return doms, base, cands, plant


def _gen_schedule(rng, hard):
    n = 8 if hard else int(rng.integers(6, 8))
    m = 4 if hard else int(rng.integers(3, 5))
    plant = rng.integers(0, m, size=n)
    doms = [(0, m - 1)] * n
    def cands():
        out = []
        for _ in range(10):
            i, j = (int(a) for a in rng.choice(n, 2, replace=False))
            if plant[i] != plant[j]:
                out.append(Constraint(NEQ, (min(i, j), max(i, j))))
            if plant[i] < plant[j]:
                out.append(Constraint(LT, (i, j)))
            i = int(rng.integers(n)); v = int(rng.integers(m))
            if v != plant[i]:
                out.append(Constraint(NEQC, (i,), (), v))
        for s in range(m):
            out.append(Constraint(CAP, (), (), s, int((plant == s).sum())))
        if rng.random() < .3:
            i = int(rng.integers(n)); out.append(Constraint(EQC, (i,), (), int(plant[i])))
        return out
    return doms, [], cands, plant


def _gen_logic(rng, hard):
    n = 12 if hard else int(rng.integers(8, 11))
    plant = rng.integers(0, 2, size=n)
    doms = [(0, 1)] * n
    def cands():
        out = []
        for _ in range(12):
            w = int(rng.integers(2, 4))
            vs = sorted(int(a) for a in rng.choice(n, w, replace=False))
            signs = tuple(int(s) for s in rng.integers(0, 2, size=w))
            c = Constraint(CLAUSE, tuple(vs), signs)
            if eval_constraint(c, plant.reshape(1, -1))[0]:
                out.append(c)
        return out
    return doms, [], cands, plant


def _gen_equations(rng, hard):
    n = 5 if hard else int(rng.integers(3, 5))
    plant = rng.integers(0, 10, size=n)
    doms = [(0, 9)] * n
    def cands():
        out = []
        for _ in range(4):
            w = int(rng.integers(2, 4)) if n >= 3 else 2
            vs = sorted(int(a) for a in rng.choice(n, min(w, n), replace=False))
            co = tuple(int(c) for c in rng.choice([-3, -2, -1, 1, 2, 3], len(vs)))
            out.append(Constraint(LIN_EQ, tuple(vs), co, int((plant[vs] * np.array(co)).sum())))
            i, j = (int(a) for a in rng.choice(n, 2, replace=False))
            if plant[i] < plant[j]:
                out.append(Constraint(LT, (i, j)))
            if plant[i] != plant[j]:
                out.append(Constraint(NEQ, (min(i, j), max(i, j))))
        return out
    return doms, [], cands, plant


def _gen_coloring(rng, hard):
    n = 9 if hard else int(rng.integers(7, 9))
    k = 3
    plant = rng.integers(0, k, size=n)
    doms = [(0, k - 1)] * n
    def cands():
        out = []
        for _ in range(10):
            i, j = (int(a) for a in rng.choice(n, 2, replace=False))
            if plant[i] != plant[j]:
                out.append(Constraint(NEQ, (min(i, j), max(i, j))))
        if rng.random() < .3:
            i = int(rng.integers(n)); out.append(Constraint(EQC, (i,), (), int(plant[i])))
        return out
    return doms, [], cands, plant


GENERATORS = {'K1_numbers': _gen_numbers, 'K2_schedule': _gen_schedule, 'K3_logic': _gen_logic,
              'K4_equations': _gen_equations, 'K5_coloring': _gen_coloring}
MAX_CONSTRAINTS = 24


def generate(cls: str, rng: np.random.Generator, hard: bool = False, tries: int = 50):
    """Returns (Problem, solutions array) with 1..MAX_SOLUTIONS solutions, or raises."""
    for _ in range(tries):
        doms, base, cands, plant = GENERATORS[cls](rng, hard)
        p = Problem(cls, len(doms), [tuple(d) for d in doms], list(base))
        seen = {c.key() for c in p.constraints}
        sols = solve_all(p)
        while len(sols) > MAX_SOLUTIONS and len(p.constraints) < MAX_CONSTRAINTS:
            pool = [c for c in cands() if c.key() not in seen]
            if not pool:
                break
            # prefer the candidate that cuts most solutions among a few random ones (keeps lists short)
            pick = [pool[int(i)] for i in rng.choice(len(pool), min(4, len(pool)), replace=False)]
            best = min(pick, key=lambda c: int(eval_constraint(c, sols).sum()))
            p.constraints.append(best); seen.add(best.key())
            sols = sols[eval_constraint(best, sols)]
        if 1 <= len(sols) <= MAX_SOLUTIONS:
            order = rng.permutation(len(p.constraints))
            p.constraints = [p.constraints[int(i)] for i in order]
            assert any((s == plant).all() for s in sols)
            return p, sols
    raise RuntimeError('generation failed for ' + cls)


# ---------------------------------------------------------------- A1: solution-independent relabelling
def relabel(p: Problem, sols: np.ndarray, rng: np.random.Generator):
    """Semantics-preserving random renaming, drawn independently of the solutions:
    variable permutation (not K1, whose order is part of the task), literal polarity flips (K3),
    colour permutation (K5).  Returns the transformed problem and its transformed solutions."""
    n = p.n
    perm = np.arange(n) if p.cls == 'K1_numbers' else rng.permutation(n)
    flip = rng.integers(0, 2, size=n) if p.cls == 'K3_logic' else np.zeros(n, int)
    col = rng.permutation(p.domains[0][1] + 1) if p.cls == 'K5_coloring' else None
    new = []
    for c in p.constraints:
        vs = tuple(int(perm[v]) for v in c.vars)
        signs, const = c.signs, c.const
        if c.ctype == CLAUSE:
            signs = tuple(int(s ^ flip[v]) for s, v in zip(c.signs, c.vars))
        if col is not None and c.ctype in (EQC, NEQC):
            const = int(col[c.const])
        if c.ctype in (NEQ, CLAUSE, LIN_EQ) and len(vs) > 1:     # order-free argument lists
            pairs = sorted(zip(vs, signs if signs else [0] * len(vs)))
            vs = tuple(a for a, _ in pairs)
            signs = tuple(b for _, b in pairs) if signs else ()
        new.append(Constraint(c.ctype, vs, signs, const, c.aux))
    S = np.empty_like(sols)
    S[:, perm] = sols
    if p.cls == 'K3_logic':
        # flip applies to ORIGINAL variable v, which now sits at column perm[v]
        for v in range(n):
            if flip[v]:
                S[:, perm[v]] = 1 - S[:, perm[v]]
    if col is not None:
        S = col[S]
    doms = [None] * n
    for v in range(n):
        doms[perm[v]] = p.domains[v]
    q = Problem(p.cls, n, doms, new)
    return q, S


def coarse_signature(p: Problem, n_solutions: int) -> str:
    """Invariant under variable renaming, K3 polarity flips and K5 colour permutation (a necessary
    condition for equivalence; used to detect possibly-equivalent instances across splits)."""
    items = []
    for c in p.constraints:
        const = None if (p.cls == 'K5_coloring' and c.ctype in (EQC, NEQC)) else c.const
        if p.cls == 'K3_logic' and c.ctype == CLAUSE:
            items.append((c.ctype, len(c.vars)))
        elif c.ctype == LIN_EQ:
            items.append((c.ctype, tuple(sorted(c.signs)), const))
        else:
            items.append((c.ctype, len(c.vars), const, c.aux))
    key = [p.cls, sorted(map(list, p.domains)), sorted(map(str, items)), int(n_solutions)]
    return hashlib.sha256(json.dumps(key).encode()).hexdigest()


# ---------------------------------------------------------------- A1: alternative construction (no plant)
def generate_alt(cls: str, rng: np.random.Generator, tries: int = 400):
    """Every constraint comes from its OWN fresh random assignment; accept 1..MAX_SOLUTIONS solutions.
    No single planted assignment shapes the constraint set."""
    for _ in range(tries):
        doms, base, cands, _ = GENERATORS[cls](rng, False)
        p = Problem(cls, len(doms), [tuple(d) for d in doms], list(base))
        seen = {c.key() for c in p.constraints}
        sols = solve_all(p)
        while len(sols) > MAX_SOLUTIONS and len(p.constraints) < MAX_CONSTRAINTS:
            for _k in range(50):
                d2, _b, c2, _ = GENERATORS[cls](rng, False)
                if [tuple(x) for x in d2] == p.domains:
                    break
            else:
                break
            pool = [c for c in c2() if c.key() not in seen]
            if not pool:
                continue
            c = pool[int(rng.integers(len(pool)))]
            p.constraints.append(c); seen.add(c.key())
            sols = sols[eval_constraint(c, sols)]
            if len(sols) == 0:
                break
        if 1 <= len(sols) <= MAX_SOLUTIONS:
            p.constraints = [p.constraints[int(i)] for i in rng.permutation(len(p.constraints))]
            return p, sols
    raise RuntimeError('alt generation failed for ' + cls)
