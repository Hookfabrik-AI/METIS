"""MÉTIS × Qwen – four-arm control experiment (Mira, 17.10.2026).

Same 12 tasks as run_01/run_02 (identical generator, seed 9901).  Four arms, all run fresh in this session:
  A  no proposal
  B  proposal = MÉTIS P2 greedy candidate (checkpoint unchanged)
  C  proposal = uniformly random value per variable inside its domain (seeded per task)
  D  proposal = best assignment found by Min-Conflicts with 256 verifier evaluations (same algorithm as the
     P2 baseline evaluate.r_mc, but returning the best assignment seen instead of only success)
B/C/D get the IDENTICAL hint text (no source name, no probabilities, no self-estimate), only in the first
message.  After a wrong answer every arm gets only the verifier feedback (same text as run_01/02).  No MÉTIS
repair.  Model, settings, parser, verifier, attempt limit unchanged from run_01/02.
Arm order rotates per task (A B C D, B C D A, ...).  All Ollama timing fields are stored per answer.
usage: python -I -B metis_qwen_4arm.py OUT_DIR [TASK_ID ...]
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np  # noqa: E402

import metis_qwen_e2e as E  # noqa: E402  (tasks, chat, parse, verify, feedback, instance helpers - unchanged)
import metis_adapter as MA  # noqa: E402
import problems as P  # noqa: E402

ARMS = ('A', 'B', 'C', 'D')
MC_BUDGET = 256
HINT = '\n\nEin ungeprüfter Lösungsvorschlag (kann falsch sein):\n'
TIMING = ('ended', 'done_reason', 'prompt_eval_count', 'eval_count', 'total_duration', 'load_duration',
          'prompt_eval_duration', 'eval_duration', 'wall_s', 'error')


def random_candidate(p, rng):
    return [int(rng.integers(lo, hi + 1)) for lo, hi in p.domains]


def min_conflicts_best(p, budget, rng):
    """evaluate.r_mc (METIS_P2) with identical moves and budget accounting; returns the assignment with the
    fewest violated conditions seen (first one on ties) and the number of verifier evaluations used."""
    calls = 0
    best = (None, 10 ** 9)

    def cost(x):
        nonlocal calls, best
        calls += 1
        k = int(P.violations(p, x).sum())
        if k < best[1]:
            best = ([int(v) for v in x], k)
        return k
    while calls < budget:
        x = np.array([rng.integers(lo, hi + 1) for lo, hi in p.domains])
        cur = cost(x); best_seen, stall = cur, 0
        while calls < budget:
            if cur == 0:
                return best[0], calls
            viol = np.nonzero(P.violations(p, x))[0]
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
    return best[0], calls


def proposal(arm, p, idx, metis):
    c0 = time.process_time()
    extra = {}
    if arm == 'B':
        cand = metis.propose(p)['candidate']
    elif arm == 'C':
        cand = random_candidate(p, np.random.default_rng(2000 + idx))
    else:
        cand, used = min_conflicts_best(p, MC_BUDGET, np.random.default_rng(1000 + idx))
        extra['verifier_evaluations'] = used
    cpu = time.process_time() - c0
    _, ok = E.verify(p, cand)                       # post-hoc bookkeeping only, never shown to Qwen
    viol = int(P.violations(p, np.array(cand)).sum())
    return {'candidate': cand, 'cpu_s': round(cpu, 6), 'correct_posthoc': ok, 'violated_posthoc': viol, **extra}


def run_arm(inst, task, idx, arm, metis):
    p = task['problem']
    r = {'arm': arm, 'attempts': []}
    text = MA.render(p)
    if arm != 'A':
        r['proposal'] = proposal(arm, p, idx, metis)
        text += HINT + E.fmt(r['proposal']['candidate'])
    messages = [{'role': 'user', 'content': text + '\n\n' + E.INSTRUCTION}]
    for k in range(E.MAX_ATTEMPTS):
        rec = E.chat(inst, messages)
        ans = E.parse(rec['content'], p.n)
        fl, ok = E.verify(p, ans)
        att = {'n': k + 1, 'prompt': messages[-1]['content'], 'answer_text': rec['content'], 'parsed': ans,
               'correct': ok, 'violated': None if fl is None else [int(i) + 1 for i in np.nonzero(fl)[0]],
               **{key: rec.get(key) for key in TIMING}}
        if arm != 'A':
            att['equals_proposal'] = ans == r['proposal']['candidate']
            att['hamming_to_proposal'] = (None if ans is None else
                                          int(sum(a != b for a, b in zip(ans, r['proposal']['candidate']))))
        r['attempts'].append(att)
        print(task['id'], arm, k + 1, 'ok' if ok else 'wrong', rec.get('ended'), rec.get('eval_count'),
              rec['wall_s'], flush=True)
        if ok or k == E.MAX_ATTEMPTS - 1:
            break
        messages += [{'role': 'assistant', 'content': rec['content']},
                     {'role': 'user', 'content': E.feedback(p, ans, fl) + '\n\n' + E.INSTRUCTION}]
    r['solved'] = r['attempts'][-1]['correct']
    r['attempts_used'] = len(r['attempts'])
    r['qwen_wall_s'] = round(sum(a['wall_s'] for a in r['attempts']), 1)
    r['qwen_output_tokens'] = sum(a.get('eval_count') or 0 for a in r['attempts'])
    return r


def main():
    out = Path(sys.argv[1])
    only = set(sys.argv[2:])
    out.mkdir(parents=True, exist_ok=False)
    tasks, skipped = E.make_tasks()
    metis = MA.Metis()
    sel = [(i, t) for i, t in enumerate(tasks) if not only or t['id'] in only]
    (out / 'tasks.json').write_text(json.dumps(
        [{'id': t['id'], 'cls': t['cls'], 'hard': t['hard'], 'n': t['problem'].n, 'domains': t['problem'].domains,
          'constraints': [[c.ctype, list(c.vars), list(c.signs), c.const, c.aux] for c in t['problem'].constraints],
          'text': MA.render(t['problem'])} for _, t in sel], ensure_ascii=False, indent=1))
    meta = {'model': E.MODEL, 'think': E.THINK, 'temperature': 0, 'seed': 0, 'num_predict': E.NUM_PREDICT,
            'deadline_s': E.DEADLINE_S, 'max_attempts': E.MAX_ATTEMPTS, 'task_seed': E.TASK_SEED,
            'arms': ARMS, 'mc_budget': MC_BUDGET, 'hint_text': HINT, 'selected_task_ids': sorted(only) or 'all',
            'skipped_known_instances': skipped, 'metis_ckpt': str(MA.CKPT), 'metis_weights_sha256': metis.sha256,
            'min_mem_available_mb': E.MIN_MEM_AVAILABLE_MB, 'mem_log': [],
            'code_sha256': {f.name: hashlib.sha256(f.read_bytes()).hexdigest()
                            for f in (HERE / 'metis_adapter.py', HERE / 'metis_qwen_e2e.py', Path(__file__).resolve())}}
    idle, why = E.ri.system_instance_idle()
    meta['system_instance_idle_before'], meta['idle_reason'] = idle, why
    meta['mem_log'].append({'at': 'start', 'mem_available_mb': E.mem_available_mb()})
    (out / 'SUMMARY.json').write_text(json.dumps(meta, indent=1))
    if not idle:
        return 2
    inst = E.ri.Instance(out / 'instance')
    (out / 'instance').mkdir()
    results = []
    try:
        err = inst.start()
        meta['instance'] = {'start_problem': err, 'port': inst.port}
        if err:
            return 2
        warm = E.chat(inst, [{'role': 'user', 'content': 'Antworte nur mit OK.'}])
        meta['warmup'] = {k: warm.get(k) for k in TIMING}
        for idx, t in sel:
            mem = E.mem_available_mb()
            meta['mem_log'].append({'at': t['id'], 'mem_available_mb': mem})
            if mem < E.MIN_MEM_AVAILABLE_MB:
                meta['stopped'] = f'MEMORY_GUARD before {t["id"]}: MemAvailable {mem} MB'
                print(meta['stopped'], flush=True)
                break
            order = ARMS[idx % 4:] + ARMS[:idx % 4]
            res = {'id': t['id'], 'cls': t['cls'], 'hard': t['hard'], 'order': list(order)}
            for arm in order:
                res[arm] = run_arm(inst, t, idx, arm, metis)
            results.append(res)
            (out / 'results.json').write_text(json.dumps(results, ensure_ascii=False, indent=1))
            (out / 'SUMMARY.json').write_text(json.dumps(meta, indent=1))
    finally:
        try:
            E.ri.http_json(inst.base, '/api/generate', {'model': E.MODEL, 'keep_alive': 0}, timeout=60)
        except Exception:                                          # noqa: BLE001
            pass
        meta['instance_stop'] = inst.stop()
        meta['system_instance_idle_after'] = E.ri.system_instance_idle()[0]
        (out / 'SUMMARY.json').write_text(json.dumps(meta, indent=1))
    print('DONE', flush=True)


if __name__ == '__main__':
    sys.exit(main())
