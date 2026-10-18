"""MÉTIS P2 x Qwen - small end-to-end functional experiment (Mira/HOOKFABRIK, 17.10.2026).

Arm A: qwen3.5:latest solves the task alone.
Arm B: the same task text + MÉTIS hints (own greedy candidate, per-variable top-2 probabilities, self-estimate;
       after a failed attempt a MÉTIS repair computed from Qwen's last answer + the verifier flags).
Both arms: identical task text, identical settings, at most MAX_ATTEMPTS answers; after each wrong answer the
external verifier (problems.violations) reports which conditions are violated - nothing else.
No solutions are generated, stored or shown; no exact solver is called.  MÉTIS weights are only loaded.
Own short-lived Ollama instance (res1_instance from the frozen RES1M package, imported unchanged); the system
instance is only checked to be idle.
usage: python -I -B metis_qwen_e2e.py OUT_DIR
"""
from __future__ import annotations

import hashlib
import http.client
import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
PKG = Path('<EXTERNAL_RES1M_RUNTIME>')
sys.path.insert(0, str(PKG))

import numpy as np  # noqa: E402

import metis_adapter as MA  # noqa: E402
import problems as P  # noqa: E402  (METIS_P2/problems.py via the adapter's path)
import res1_instance as ri  # noqa: E402
import resource_profile  # noqa: E402

MODEL = 'qwen3.5:latest'
THINK = False
NUM_PREDICT = 4096
DEADLINE_S = 600
MAX_ATTEMPTS = 3
TASK_SEED = 9901
PLAN = [('K1_numbers', False, 2), ('K2_schedule', False, 2), ('K3_logic', False, 2), ('K4_equations', False, 2),
        ('K1_numbers', True, 1), ('K2_schedule', True, 1), ('K3_logic', True, 1), ('K4_equations', True, 1)]
PRIOR_DATA = [Path('<LOCAL_METIS_P2>/data_p2'),
              Path('<LOCAL_P1>/data_p1')]

INSTRUCTION = ('Gib am Ende deiner Antwort genau eine Zeile in diesem Format aus:\n'
               'LÖSUNG: x0=<Zahl>, x1=<Zahl>, ...')


def make_tasks():
    """New instances (fresh seed), relabelled like the datasets; any instance whose canonical form occurs in a
    P1 or P2 split is skipped.  The planted/enumerated solutions returned by the generator are discarded."""
    seen = set()
    for d in PRIOR_DATA:
        for f in d.glob('*.jsonl'):
            for line in f.read_text().splitlines():
                seen.add(json.loads(line)['canonical'])
    rng = np.random.default_rng(TASK_SEED)
    tasks, skipped = [], 0
    for cls, hard, k in PLAN:
        got = 0
        while got < k:
            p, sols = P.generate(cls, rng, hard)
            p, sols = P.relabel(p, sols, rng)
            del sols                                            # never used, never stored
            if p.canonical() in seen:
                skipped += 1
                continue
            seen.add(p.canonical())
            tasks.append({'id': f'T{len(tasks) + 1:02d}', 'cls': cls, 'hard': hard, 'problem': p})
            got += 1
    return tasks, skipped


def fmt(x):
    return ', '.join(f'x{i}={v}' for i, v in enumerate(x))


def parse(text, n):
    lines = [ln for ln in text.splitlines() if re.search(r'L[ÖO]SUNG\s*:', ln, re.I)]
    if not lines:
        return None
    pairs = dict((int(i), int(v)) for i, v in re.findall(r'x\s*(\d+)\s*=\s*(-?\d+)', lines[-1]))
    if sorted(pairs) != list(range(n)):
        return None
    return [pairs[i] for i in range(n)]


def metis_block(p, prop):
    lines = [f'  x{i}: {a} ({pa:.0%}), sonst {b} ({pb:.0%})' for i, ((a, pa), (b, pb)) in enumerate(prop['top2'])]
    return ('\n\nHinweis von MÉTIS (ein kleines, auf solche Aufgaben trainiertes neuronales Modell). '
            'Der Vorschlag ist NICHT geprüft und kann falsch sein:\n'
            f'MÉTIS-Vorschlag: {fmt(prop["candidate"])}\n'
            f'Eigene Sicherheit von MÉTIS, dass der Vorschlag vollständig stimmt: {prop["p_hat"]:.0%}\n'
            'Wahrscheinlichste Werte je Variable laut MÉTIS:\n' + '\n'.join(lines))


def feedback(p, ans, flags):
    if ans is None:
        return 'Prüfer: Keine auswertbare LÖSUNG-Zeile mit allen Variablen gefunden.'
    bad = [f'B{k + 1}: {MA.render_constraint(c, p.n)}' for k, c in enumerate(p.constraints) if flags[k]]
    out_dom = [f'x{i}' for i, (lo, hi) in enumerate(p.domains) if not lo <= ans[i] <= hi]
    msg = 'Prüfer: Deine Lösung ist falsch.'
    if out_dom:
        msg += ' Außerhalb des Wertebereichs: ' + ', '.join(out_dom) + '.'
    return msg + ' Verletzte Bedingungen:\n' + '\n'.join(bad)


def chat(inst, messages):
    body = {'model': MODEL, 'stream': True, 'think': THINK, 'messages': messages,
            'options': {'temperature': 0, 'seed': 0, 'num_ctx': resource_profile.num_ctx_for(MODEL),
                        'num_predict': NUM_PREDICT}}
    rec = {'content': '', 'ended': None}
    t0 = time.monotonic()
    conn = http.client.HTTPConnection('127.0.0.1', inst.port, timeout=DEADLINE_S)
    try:
        conn.request('POST', '/api/chat', json.dumps(body), {'Content-Type': 'application/json'})
        resp = conn.getresponse()
        while True:
            if time.monotonic() - t0 > DEADLINE_S:
                rec['ended'] = 'DEADLINE_REACHED_INCOMPLETE'
                break
            line = resp.readline()
            if not line:
                rec['ended'] = rec['ended'] or 'STREAM_CLOSED_WITHOUT_DONE'
                break
            d = json.loads(line)
            if 'error' in d:
                rec['ended'], rec['error'] = 'BACKEND_ERROR', d['error']
                break
            rec['content'] += (d.get('message') or {}).get('content') or ''
            if d.get('done'):
                rec['ended'] = 'DONE'
                for k in ('done_reason', 'prompt_eval_count', 'eval_count', 'total_duration', 'load_duration',
                          'prompt_eval_duration', 'eval_duration'):
                    rec[k] = d.get(k)
                break
    except Exception as exc:                                       # noqa: BLE001
        rec['ended'], rec['error'] = 'CLIENT_ERROR', type(exc).__name__
    finally:
        conn.close()
    rec['wall_s'] = round(time.monotonic() - t0, 1)
    if rec.get('done_reason') == 'length':
        rec['ended'] = 'OUTPUT_LIMIT_REACHED_INCOMPLETE'
    return rec


def verify(p, x):
    if x is None:
        return None, False
    fl = P.violations(p, np.array(x))
    return fl, bool(P.in_domain(p, x) and not fl.any())


def run_arm(inst, metis, task, arm):
    p = task['problem']
    text = MA.render(p)
    r = {'arm': arm, 'attempts': [], 'metis': []}
    first = text
    if arm == 'B':
        prop = metis.propose(p)
        fl_m, ok_m = verify(p, prop['candidate'])                 # post-hoc bookkeeping only, never shown to Qwen
        r['metis'].append({'kind': 'propose', **prop, 'correct_posthoc': ok_m})
        first += metis_block(p, prop)
    messages = [{'role': 'user', 'content': first + '\n\n' + INSTRUCTION}]
    for k in range(MAX_ATTEMPTS):
        rec = chat(inst, messages)
        ans = parse(rec['content'], p.n)
        fl, ok = verify(p, ans)
        att = {'n': k + 1, 'prompt': messages[-1]['content'], 'answer_text': rec['content'], 'parsed': ans,
               'correct': ok, 'violated': None if fl is None else [int(i) + 1 for i in np.nonzero(fl)[0]],
               **{key: rec.get(key) for key in ('ended', 'done_reason', 'prompt_eval_count', 'eval_count',
                                               'total_duration', 'eval_duration', 'wall_s', 'error')}}
        if arm == 'B':
            att['equals_a_metis_candidate'] = ans is not None and any(ans == m['candidate'] for m in r['metis'])
            att['hamming_to_last_metis'] = (None if ans is None else
                                            int(sum(a != b for a, b in zip(ans, r['metis'][-1]['candidate']))))
        r['attempts'].append(att)
        print(task['id'], arm, k + 1, 'ok' if ok else 'wrong', rec.get('ended'), rec.get('eval_count'),
              rec['wall_s'], flush=True)
        if ok or k == MAX_ATTEMPTS - 1:
            break
        msg = feedback(p, ans, fl)
        if arm == 'B':
            if ans is not None and all(0 <= v < 16 for v in ans):
                rep = metis.repair(p, ans, fl)
                fl_m, ok_m = verify(p, rep['candidate'])
                r['metis'].append({'kind': 'repair', **rep, 'from_qwen_attempt': k + 1, 'correct_posthoc': ok_m})
                msg += ('\n\nMÉTIS hat aus deiner letzten Antwort und diesen Fehlermarken einen neuen, NICHT geprüften '
                        f'Vorschlag berechnet: {fmt(rep["candidate"])}')
            else:
                r['metis'].append({'kind': 'repair_skipped', 'reason': 'Qwen answer not usable as MÉTIS input'})
        messages += [{'role': 'assistant', 'content': rec['content']},
                     {'role': 'user', 'content': msg + '\n\n' + INSTRUCTION}]
    r['solved'] = r['attempts'][-1]['correct']
    r['attempts_used'] = len(r['attempts'])
    r['qwen_wall_s'] = round(sum(a['wall_s'] for a in r['attempts']), 1)
    r['qwen_output_tokens'] = sum(a.get('eval_count') or 0 for a in r['attempts'])
    return r


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=False)
    tasks, skipped = make_tasks()
    metis = MA.Metis()
    (out / 'tasks.json').write_text(json.dumps(
        [{'id': t['id'], 'cls': t['cls'], 'hard': t['hard'], 'n': t['problem'].n, 'domains': t['problem'].domains,
          'constraints': [[c.ctype, list(c.vars), list(c.signs), c.const, c.aux] for c in t['problem'].constraints],
          'text': MA.render(t['problem'])} for t in tasks], ensure_ascii=False, indent=1))
    meta = {'model': MODEL, 'think': THINK, 'temperature': 0, 'seed': 0, 'num_predict': NUM_PREDICT,
            'deadline_s': DEADLINE_S, 'max_attempts': MAX_ATTEMPTS, 'task_seed': TASK_SEED,
            'tasks': len(tasks), 'skipped_known_instances': skipped,
            'metis_ckpt': str(MA.CKPT), 'metis_weights_sha256': metis.sha256,
            'code_sha256': {f.name: hashlib.sha256(f.read_bytes()).hexdigest()
                            for f in (HERE / 'metis_adapter.py', Path(__file__).resolve())}}
    idle, why = ri.system_instance_idle()
    meta['system_instance_idle_before'], meta['idle_reason'] = idle, why
    if not idle:
        (out / 'SUMMARY.json').write_text(json.dumps(meta, indent=1))
        return 2
    inst = ri.Instance(out / 'instance')
    (out / 'instance').mkdir()
    results = []
    try:
        err = inst.start()
        meta['instance'] = {'start_problem': err, 'port': inst.port}
        if err:
            return 2
        warm = chat(inst, [{'role': 'user', 'content': 'Antworte nur mit OK.'}])   # model load outside the arms
        meta['warmup'] = {k: warm.get(k) for k in ('ended', 'wall_s', 'load_duration')}
        for i, t in enumerate(tasks):
            order = ('A', 'B') if i % 2 == 0 else ('B', 'A')
            res = {'id': t['id'], 'cls': t['cls'], 'hard': t['hard']}
            for arm in order:
                res[arm] = run_arm(inst, metis, t, arm)
            results.append(res)
            (out / 'results.json').write_text(json.dumps(results, ensure_ascii=False, indent=1))
    finally:
        try:
            ri.http_json(inst.base, '/api/generate', {'model': MODEL, 'keep_alive': 0}, timeout=60)
        except Exception:                                          # noqa: BLE001
            pass
        meta['instance_stop'] = inst.stop()
        meta['system_instance_idle_after'] = ri.system_instance_idle()[0]
        meta['metis_cpu_s_total'] = round(metis.cpu_s, 4)
        (out / 'SUMMARY.json').write_text(json.dumps(meta, indent=1))
    print('DONE', flush=True)


if __name__ == '__main__':
    sys.exit(main())
