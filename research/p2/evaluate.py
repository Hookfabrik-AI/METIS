"""P2 (MÉTIS) final evaluation - run ONCE after all training.  Pre-registered: 07_PILOT_PLAN_P2.md
(P1 criteria C1-C4 unchanged + C5/C6: slot-binding fix vs archived P1 models on K4/K3).
Order: dev-only selection of rule and c FIRST, then every test computation (Codex P1 note).
Refuses to run if OUT_JSON or its .started marker exists (one-shot guard).
usage: python -I -B evaluate.py DATA_DIR RUNS_DIR P1_DIR OUT_JSON
RUNS_DIR/seed{s}/A/best.pt, seed{s}/B/best.pt, seed0/C/best.pt; P1_DIR/runs_p1/seed{s}/B/best.pt, P1_DIR/data_p1
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # -I drops the script dir from sys.path

import numpy as np
import torch

import cog
import dataset as D
import model as M
import problems as P

UNTRAINED_SEED = 424242
SEEDS = (0, 1, 2)
TEST_SETS = ('test', 'test_hard', 'test_alt', 'test_k5', 'test_k5_hard')
MC_BUDGETS = (4, 16, 64, 256)
CHECK_COST, WRONG, RIGHT, ROUNDS = 0.05, -3.0, 1.0, 3
NBOOT = 10000


def load_set(data, name):
    rows = D.load(data / f'{name}.jsonl')
    ps = [p for p, _ in rows]
    return ps, [M.encode_static(p) for p in ps]


def net_from(path=None):
    torch.manual_seed(UNTRAINED_SEED)
    net = M.Net()
    if path:
        net.load_state_dict(torch.load(path, weights_only=True))
    return net.eval()


def greedy_ok(net, ps, ss):
    a = []
    for c in cog.chunks(len(ss)):
        a.extend(cog.decode(net, ss[c]))
    return cog.verify(ps, a)[1], a


# ------------------------------------------------------------------ rule baselines
def r_rand(ps, rng, struct=False):
    ok = []
    for p in ps:
        if struct and p.cls == 'K1_numbers':
            lo, hi = p.domains[0]
            x = np.sort(rng.choice(np.arange(lo, hi + 1), p.n, replace=False))
        else:
            x = np.array([rng.integers(lo, hi + 1) for lo, hi in p.domains])
        ok.append(not P.violations(p, x).any())
    return np.array(ok)


def r_mc(p, budget, rng):
    """Min-Conflicts (A6).  Every full verifier evaluation counts against the budget."""
    calls = 0
    def cost(x):
        nonlocal calls
        calls += 1
        return int(P.violations(p, x).sum())
    while calls < budget:
        x = np.array([rng.integers(lo, hi + 1) for lo, hi in p.domains])
        cur = cost(x); best_seen, stall = cur, 0
        while calls < budget:
            if cur == 0:
                return True
            viol = np.nonzero(P.violations(p, x))[0]          # reuse of the last evaluation (same x), not a new call
            c = p.constraints[int(rng.choice(viol))]
            vs = list(c.vars) if c.vars else list(range(p.n))
            v = int(rng.choice(vs))
            lo, hi = p.domains[v]
            scores = []
            for val in range(lo, hi + 1):
                if calls >= budget:
                    break
                y = x.copy(); y[v] = val
                scores.append((cost(y), rng.random(), val))
            if not scores:
                break
            s, _, val = min(scores)
            x[v] = val; cur = s
            if cur < best_seen:
                best_seen, stall = cur, 0
            else:
                stall += 1
                if stall >= 50:
                    break
    return cur == 0


# ------------------------------------------------------------------ steering (A4/A5)
def steering_states(net, ps, ss, seed):
    """Everything a policy may use (p_hat, q_hat, conf, violation count after a check) plus the
    outcomes of executing each strategy (seeded identically, independent of the policy choice)."""
    a1 = []; [a1.extend(cog.decode(net, ss[c])) for c in cog.chunks(len(ss))]
    fl, ok = cog.verify(ps, a1)
    conf = np.concatenate([cog.confidence(net, ss[c]) for c in cog.chunks(len(ss))])
    with torch.no_grad():
        ph = np.concatenate([torch.sigmoid(net.heads(M.collate(ss[c], a1[c], None, M.MODE_PREV))[0]).numpy()
                             for c in cog.chunks(len(ss))])
        qh = np.concatenate([torch.sigmoid(net.heads(M.collate(ss[c], a1[c], fl[c], M.MODE_FB))[1]).numpy()
                             for c in cog.chunks(len(ss))])
    out = {}
    for strat in ('rep', 'new'):
        out[strat] = cog.strategy_rollout(net, ps, ss, a1, fl, strat, rounds=ROUNDS, seed=seed)
    nviol = np.array([int(f.sum()) for f in fl])
    return {'ok': ok, 'conf': conf, 'p': ph, 'q': qh, 'nviol': nviol, 'roll': out}


def run_policy(st, d1, d2, head_d1=0, head_d2=0, check_cost=None):
    """d1(i) in {'conclude','abstain','check'}; d2(i) in {'rep','new','abstain'} (only after a failed check).
    head_d1/head_d2: extra trunk forward passes the policy needs for its decision (learned heads: 1 each).
    Returns per-instance utility, raw counts, per-instance checks/forwards/correct and action counts."""
    CHECK_COST_ = CHECK_COST if check_cost is None else check_cost
    n = len(st['ok']); u = np.zeros(n)
    cnt = {'concl_right': 0, 'concl_wrong': 0, 'abstain': 0, 'checks': 0, 'solved_after_check': 0}
    act = {'d1_conclude': 0, 'd1_abstain': 0, 'd1_check': 0, 'd2_rep': 0, 'd2_new': 0, 'd2_abstain': 0}
    chk = np.zeros(n, int); fwd = np.ones(n, int); right = np.zeros(n, bool)   # a1 = 1 forward
    for i in range(n):
        a = d1(i); fwd[i] += head_d1; act['d1_' + a] += 1
        if a == 'conclude':
            right[i] = bool(st['ok'][i])
            u[i] = RIGHT if st['ok'][i] else WRONG
            cnt['concl_right' if st['ok'][i] else 'concl_wrong'] += 1
            continue
        if a == 'abstain':
            cnt['abstain'] += 1
            continue
        u[i] -= CHECK_COST_; cnt['checks'] += 1; chk[i] += 1
        if st['ok'][i]:
            u[i] += RIGHT; cnt['solved_after_check'] += 1; right[i] = True
            continue
        b = d2(i); fwd[i] += head_d2; act['d2_' + b] += 1
        if b == 'abstain':
            cnt['abstain'] += 1
            continue
        solved, used = st['roll'][b]
        u[i] -= CHECK_COST_ * used[i]; cnt['checks'] += int(used[i]); chk[i] += int(used[i]); fwd[i] += int(used[i])
        if solved[i]:
            u[i] += RIGHT; cnt['solved_after_check'] += 1; right[i] = True
        else:
            cnt['abstain'] += 1
    return u, cnt, {'checks': chk, 'forwards': fwd, 'right': right, 'actions': act}


def learned_policy(st, c):
    def d1(i):
        p = st['p'][i]
        return ['conclude', 'abstain', 'check'][int(np.argmax([4 * p - 3, 0.0, p + (1 - p) * c - CHECK_COST]))]
    def d2(i):
        qr, qn = st['q'][i]
        ev = [q - CHECK_COST * ROUNDS * (1 - q / 2) for q in (qr, qn)] + [0.0]
        return ['rep', 'new', 'abstain'][int(np.argmax(ev))]
    return d1, d2


def rule_grid():
    d1s = [('always_check', None), ('always_conclude', None)] + [('conf', t) for t in np.round(np.arange(0.5, 1.0, 0.02), 2)]
    d2s = [('rep', None), ('new', None), ('abstain', None)] + [('viol', m) for m in range(1, 6)]
    return [(a, b) for a in d1s for b in d2s]


def rule_policy(st, rule):
    (k1, t), (k2, m) = rule
    def d1(i):
        if k1 == 'always_check':
            return 'check'
        if k1 == 'always_conclude':
            return 'conclude'
        return 'conclude' if st['conf'][i] >= t else 'check'
    def d2(i):
        if k2 == 'viol':
            return 'rep' if st['nviol'][i] <= m else 'new'
        return k2
    return d1, d2


# ------------------------------------------------------------------ statistics
def boot(diff, ps, rng, n=NBOOT):
    """Class-stratified, equal class weights, paired.  Returns mean, one-sided 95% lower bound, p (share <= 0)."""
    cls = np.array([p.cls for p in ps]); groups = [np.nonzero(cls == c)[0] for c in sorted(set(cls))]
    mean = float(np.mean([diff[g].mean() for g in groups]))
    bs = np.zeros(n)
    for c, g in enumerate(groups):
        bs += diff[g][rng.integers(0, len(g), (n, len(g)))].mean(1)
    bs /= len(groups)
    return {'mean': mean, 'lower95': float(np.quantile(bs, 0.05)), 'p': float((bs <= 0).mean())}


def per_class(x, ps):
    cls = np.array([p.cls for p in ps])
    return {c: float(np.asarray(x, float)[cls == c].mean()) for c in sorted(set(cls))}


def cpu_costs(net, ps, ss, rng):
    """Real CPU cost per unit (seconds, process CPU time over all threads, and wall time):
    one trunk forward per instance (batched 512 and batch=1), one verifier call, Min-Conflicts per budget."""
    def tm(fn, reps):
        c0, w0 = time.process_time(), time.perf_counter(); fn(); return ((time.process_time() - c0) / reps,
                                                                           (time.perf_counter() - w0) / reps)
    n = len(ps); out = {}
    out['forward_batched_512'] = tm(lambda: [cog.decode(net, ss[c]) for c in cog.chunks(n)], n)
    k = min(300, n)
    out['forward_batch1'] = tm(lambda: [cog.decode(net, [ss[i]]) for i in range(k)], k)
    a = []; [a.extend(cog.decode(net, ss[c])) for c in cog.chunks(n)]
    out['verifier_call'] = tm(lambda: cog.verify(ps, a), n)
    for bud in MC_BUDGETS:
        out[f'min_conflicts_{bud}'] = tm(lambda: [r_mc(p, bud, rng) for p in ps[:k]], k)
    return {key: {'cpu_s': v[0], 'wall_s': v[1]} for key, v in out.items()}


def holm(pvals: dict, alpha=0.05):
    order = sorted(pvals, key=pvals.get); res = {}; stop = False
    for k, name in enumerate(order):
        thr = alpha / (len(order) - k)
        ok = (not stop) and pvals[name] <= thr
        stop = stop or not ok
        res[name] = {'p': pvals[name], 'threshold': thr, 'reject_null': ok}
    return res


def load_p1_model_module(p1dir):
    spec = importlib.util.spec_from_file_location('model_p1', p1dir / 'model.py')
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def p1_net(M1, path):
    net = M1.Net(); net.load_state_dict(torch.load(path, weights_only=True)); return net.eval()


def greedy_ok_p1(M1, net, ps):
    a = []
    for c in cog.chunks(len(ps)):
        with torch.no_grad():
            lg, _, _ = net.logits(M1.collate([M1.encode_static(p) for p in ps[c]]))
        x = lg.argmax(-1).numpy(); a.extend(x[b, :p.n].copy() for b, p in enumerate(ps[c]))
    return cog.verify(ps, a)[1]


def fb4_p1(M1, net, ps, seed):
    """P1 model in the identical FB@4 protocol (same seeds as cog.success_at_k)."""
    succ = np.zeros(len(ps), bool)
    for sl in cog.chunks(len(ps)):
        pp = ps[sl]; ss = [M1.encode_static(p) for p in pp]
        gen = torch.Generator().manual_seed(seed * 1000003 + sl.start)
        with torch.no_grad():
            def dec(prev=None, flags=None, mode=0, sample=False):
                lg, _, _ = net.logits(M1.collate(ss, prev, flags, mode))
                if sample:
                    pr = torch.softmax(lg, -1); B, V, K = pr.shape
                    x = torch.multinomial(pr.reshape(B * V, K), 1, generator=gen).reshape(B, V)
                else:
                    x = lg.argmax(-1)
                x = x.numpy(); return [x[b, :s['n']].copy() for b, s in enumerate(ss)]
            a = dec(); fl, ok = cog.verify(pp, a); s = ok.copy()
            for _ in range(3):
                a = dec(a, fl, M1.MODE_FB, True); fl, ok = cog.verify(pp, a); s |= ok
        succ[sl] = s
    return succ


def main():
    data, runs, p1dir, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
    marker = out.with_suffix('.started')
    if out.exists() or marker.exists():
        sys.exit(f'REFUSED: {out} or {marker} exists - the test sets are evaluated only once')
    out.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(time.strftime('%Y-%m-%d %H:%M:%S'))
    torch.set_num_threads(8)
    t0 = time.time(); rng = np.random.default_rng(777)
    R = {'started': time.strftime('%Y-%m-%d %H:%M:%S'), 'sets': {}}
    PER = {}                                                  # per-instance outcomes (saved as npz)

    # --- 1. C4 selection on DEV ONLY, frozen before any test set is loaded
    devp, devs = load_set(data, 'dev')
    C = net_from(runs / 'seed0' / 'C' / 'best.pt')
    sd = steering_states(C, devp, devs, seed=91)
    failed = ~sd['ok']
    d2_dev = learned_policy(sd, 0.0)[1]
    c_vals = []
    for i in np.nonzero(failed)[0]:
        b = d2_dev(i)
        if b == 'abstain':
            c_vals.append(0.0)
        else:
            solved, used = sd['roll'][b]
            c_vals.append(RIGHT * solved[i] - CHECK_COST * used[i])
    c = float(np.mean(c_vals)) if c_vals else 0.0
    grid = rule_grid()
    dev_util = [float(run_policy(sd, *rule_policy(sd, r))[0].mean()) for r in grid]
    best_rule = grid[int(np.argmax(dev_util))]
    R['steering'] = {'c_from_dev': c, 'best_rule_from_dev': str(best_rule), 'best_rule_dev_utility': max(dev_util),
                     'learned_dev_utility': float(run_policy(sd, *learned_policy(sd, c), 1, 1)[0].mean()),
                     'frozen_before_test': True, 'frozen_at_s': round(time.time() - t0)}
    print('steering frozen on dev', json.dumps(R['steering']), flush=True)

    # --- 2. test sets (loaded only now)
    sets = {n: load_set(data, n) for n in TEST_SETS}
    U = net_from(None)
    R['untrained_sha256'] = M.weights_sha256(U)

    # --- C2 / C3 for every seed, every test set (claims use 'test' only)
    for s in SEEDS:
        A = net_from(runs / f'seed{s}' / 'A' / 'best.pt'); B = net_from(runs / f'seed{s}' / 'B' / 'best.pt')
        for name, (ps, ss) in sets.items():
            r = R['sets'].setdefault(name, {}).setdefault(f'seed{s}', {})
            okU, _ = greedy_ok(U, ps, ss); okA, _ = greedy_ok(A, ps, ss); okB, _ = greedy_ok(B, ps, ss)
            fb, vfb = cog.success_at_k(B, ps, ss, 'FB', seed=s)
            pv, vpv = cog.success_at_k(B, ps, ss, 'PREV', seed=s)
            nf, vnf = cog.success_at_k(B, ps, ss, 'NOFB', seed=s)
            fa, _ = cog.success_at_k(A, ps, ss, 'FB', seed=s)
            arr = {'U_1': okU, 'A_1': okA, 'L_1': okB, 'FB_4': fb, 'PREV_4': pv, 'NOFB_4': nf, 'A_FB_4': fa}
            for k, v in arr.items():
                PER[f'{name}/seed{s}/{k}'] = np.asarray(v, bool)
            r['rates'] = {k: per_class(v, ps) for k, v in arr.items()}
            r['last_violations_mean'] = {'FB': float(vfb.mean()), 'PREV': float(vpv.mean()), 'NOFB': float(vnf.mean())}
            r['C2_L1_minus_U'] = boot(okB.astype(float) - okU, ps, rng)
            r['C3i_FB_minus_PREV'] = boot(fb.astype(float) - pv, ps, rng)
            r['C3ii_FB_B_minus_FB_A'] = boot(fb.astype(float) - fa, ps, rng)
            r['FB_minus_NOFB'] = boot(fb.astype(float) - nf, ps, rng)
            print(name, 'seed', s, json.dumps({k: round(float(np.mean(list(v.values()))), 3) for k, v in r['rates'].items()}), flush=True)

    # --- C5 / C6: slot-binding fix vs archived P1 models (same procedure, unfixed encoder), P2 'test',
    #     restricted to instances whose canonical form does not occur in ANY P1 split.  (The coarse signature
    #     is too coarse for K3: only 3/1000 K3 test instances avoid every P1 coarse key.)  Remaining
    #     renamed copies of P1 training instances could only favour P1, i.e. the comparison is conservative.
    M1 = load_p1_model_module(p1dir)
    p1_canon, p1_coarse = set(), set()
    for f in sorted((p1dir / 'data_p1').glob('*.jsonl')):
        for line in f.read_text().splitlines():
            d = json.loads(line); p1_canon.add(d['canonical']); p1_coarse.add(d['coarse'])
    ps, ss = sets['test']
    sols_n = [len(x) for _, x in D.load(data / 'test.jsonl')]
    fresh = np.array([p.canonical() not in p1_canon for p in ps])
    coarse_fresh = np.array([P.coarse_signature(p, k) not in p1_coarse for p, k in zip(ps, sols_n)])
    R['p1_comparison'] = {'subset_rule': 'P2 test instances whose canonical form is in no P1 split',
                          'subset_share_per_class': per_class(fresh, ps), 'n_total': int(fresh.sum()),
                          'coarse_fresh_share_per_class (descriptive)': per_class(coarse_fresh, ps)}
    for s in SEEDS:
        B1 = p1_net(M1, p1dir / 'runs_p1' / f'seed{s}' / 'B' / 'best.pt')
        ok1 = greedy_ok_p1(M1, B1, ps); fb1 = fb4_p1(M1, B1, ps, seed=s)
        ok2 = PER[f'test/seed{s}/L_1']; fb2 = PER[f'test/seed{s}/FB_4']
        PER[f'test/seed{s}/P1_L_1'] = ok1; PER[f'test/seed{s}/P1_FB_4'] = fb1
        r = R['p1_comparison'][f'seed{s}'] = {'rates_all': {'P1_L_1': per_class(ok1, ps), 'P2_L_1': per_class(ok2, ps),
                                                            'P1_FB_4': per_class(fb1, ps), 'P2_FB_4': per_class(fb2, ps)}}
        for crit, cls in (('C5_K4', 'K4_equations'), ('C6_K3', 'K3_logic')):
            m = fresh & np.array([p.cls == cls for p in ps]); sub = [ps[i] for i in np.nonzero(m)[0]]
            r[crit + '_L1_P2_minus_P1'] = boot(ok2[m].astype(float) - ok1[m], sub, rng)
            r[crit + '_FB4_P2_minus_P1'] = boot(fb2[m].astype(float) - fb1[m], sub, rng)
        print('p1 comparison seed', s, json.dumps({k: v['mean'] for k, v in r.items() if isinstance(v, dict) and 'mean' in v}), flush=True)

    # --- rule baselines (explorative), on every set
    for name, (ps_, ss_) in sets.items():
        b = R['sets'][name]['baselines'] = {}
        b['R_rand'] = per_class(r_rand(ps_, np.random.default_rng(1)), ps_)
        b['R_rand_struct'] = per_class(r_rand(ps_, np.random.default_rng(1), struct=True), ps_)
        for bud in MC_BUDGETS:
            mrng = np.random.default_rng(bud)
            b[f'R_mc_{bud}'] = per_class([r_mc(p, bud, mrng) for p in ps_], ps_)
        print(name, 'baselines', json.dumps({k: round(float(np.mean(list(v.values()))), 3) for k, v in b.items()}), flush=True)

    # --- C4 steering test episodes with the frozen rule / c
    ps, ss = sets['test']
    st = steering_states(C, ps, ss, seed=92)
    uL, cL, xL = run_policy(st, *learned_policy(st, c), 1, 1)
    uR, cR, xR = run_policy(st, *rule_policy(st, best_rule))
    u0L = run_policy(st, *learned_policy(st, c), 1, 1, check_cost=0.0)[0]
    u0R = run_policy(st, *rule_policy(st, best_rule), check_cost=0.0)[0]
    for k in ('checks', 'forwards', 'right'):
        PER[f'steer/learned/{k}'] = xL[k]; PER[f'steer/rule/{k}'] = xR[k]
    PER['steer/learned/utility'] = uL; PER['steer/rule/utility'] = uR
    R['steering'].update({'test_learned_utility': per_class(uL, ps), 'test_rule_utility': per_class(uR, ps),
                          'test_learned_counts': cL, 'test_rule_counts': cR,
                          'test_learned_actions': xL['actions'], 'test_rule_actions': xR['actions'],
                          'correct_per_class': {'learned': per_class(xL['right'], ps), 'rule': per_class(xR['right'], ps)},
                          'checks_per_task': {'learned': per_class(xL['checks'], ps), 'rule': per_class(xR['checks'], ps)},
                          'forwards_per_task': {'learned': per_class(xL['forwards'], ps), 'rule': per_class(xR['forwards'], ps)},
                          'correct_lost_learned_vs_rule': int(xR['right'].sum() - xL['right'].sum()),
                          'checks_saved_learned_vs_rule': int(xR['checks'].sum() - xL['checks'].sum()),
                          'forwards_saved_learned_vs_rule': int(xR['forwards'].sum() - xL['forwards'].sum()),
                          'C4_learned_minus_rule': boot(uL - uR, ps, rng),
                          'sensitivity_check_cost_0': boot(u0L - u0R, ps, rng),
                          'p_hat_brier_test': float(((st['p'] - st['ok']) ** 2).mean()),
                          'p_const_brier_test': float(((sd['ok'].mean() - st['ok']) ** 2).mean())})
    for strat in ('rep', 'new'):
        R['steering'][f'counterfactual_{strat}_solved_rate_on_failed'] = float(st['roll'][strat][0][~st['ok']].mean())

    # --- real CPU costs (explorative): unit costs measured on 'test' with the B0 model and the learned C0 model
    B0 = net_from(runs / 'seed0' / 'B' / 'best.pt')
    R['cpu_costs'] = {'threads': torch.get_num_threads(), 'units': cpu_costs(B0, ps, ss, np.random.default_rng(5))}
    R['cpu_costs']['note'] = ('steering CPU per task = forwards * forward_cost + checks * verifier_cost; '
                              'see 07_PILOT_PLAN_P2.md for the reported comparison')

    # --- acceptance: C2, C3, C5, C6 must hold in all seeds (p = worst seed); Holm over C2..C6
    tt = R['sets']['test']; pc = R['p1_comparison']
    pv_ = {'C2': max(tt[f'seed{s}']['C2_L1_minus_U']['p'] for s in SEEDS),
           'C3': max(max(tt[f'seed{s}']['C3i_FB_minus_PREV']['p'], tt[f'seed{s}']['C3ii_FB_B_minus_FB_A']['p']) for s in SEEDS),
           'C4': R['steering']['C4_learned_minus_rule']['p'],
           'C5': max(pc[f'seed{s}']['C5_K4_L1_P2_minus_P1']['p'] for s in SEEDS),
           'C6': max(pc[f'seed{s}']['C6_K3_L1_P2_minus_P1']['p'] for s in SEEDS)}
    R['acceptance'] = {'holm': holm(pv_),
                       'note': 'C1 descriptive (training logs); p = worst seed for C2/C3/C5/C6; C3 = max over (i),(ii)'}
    R['elapsed_s'] = round(time.time() - t0)
    np.savez_compressed(out.with_suffix('.per_instance.npz'), **{k.replace('/', '__'): v for k, v in PER.items()})
    out.write_text(json.dumps(R, indent=1))
    print(json.dumps(R['acceptance'], indent=1))


if __name__ == '__main__':
    main()
