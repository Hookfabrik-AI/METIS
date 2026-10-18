"""P2 training (MÉTIS): unchanged P1 procedure - stage A (solve), B (reflection, on-policy), C (self-assessment /
strategy heads, trunk frozen) - with the P1 protocol deviations corrected (Mira P2 §2, Codex P1 review):
  * best.pt is saved on EVERY strict dev improvement (ties -> earlier); the plateau counter is separate
    (reset only by an improvement > MIN_DELTA over the last reset value);
  * the wall-time limit is checked after every step, with a reserve of the last measurement's duration,
    so that the final measurement still finishes inside the limit;
  * instability = non-finite loss, or the last 3 measured train losses all > 3x the minimum measured loss (A7);
  * stage C measures every 500 steps like A/B and uses the same rules.
Dev-only measurement, checkpoint + hash log.
usage: python -I -B train.py DATA_DIR RUN_DIR SEED STAGE [INIT_CKPT]
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # -I drops the script dir from sys.path

import numpy as np
import torch
import torch.nn.functional as F

import cog
import dataset as D
import model as M
import problems as P

EVAL_EVERY = 500
PATIENCE, MIN_DELTA = 5, 0.005
WALL = {'A': 3600, 'B': 3600, 'C': 1800}
MIN_DELTA_C = 0.001                 # stage C metric is a Brier score (lower = better)
BATCH = 128
LR = {'A': 3e-4, 'B': 1.5e-4, 'C': 1e-3}
KEEP_EVERY = 4
CLASSES = D.TRAIN_CLASSES


def code_hash():
    h = hashlib.sha256()
    for f in ('problems.py', 'dataset.py', 'model.py', 'cog.py', 'train.py'):  # unchanged list
        h.update((Path(__file__).parent / f).read_bytes())
    return h.hexdigest()


def class_mean(values, problems):
    v = np.asarray(values, float)
    return float(np.mean([v[[p.cls == c for p in problems]].mean() for c in sorted({p.cls for p in problems})]))


def target_most_likely(lg, sols_list, n_list):
    """A2: per instance, the valid TRAINING solution with max summed log-prob under the current model
    (no gradient through the choice; ties -> lowest index)."""
    lp = torch.log_softmax(lg.detach(), -1)
    tgt = torch.full(lg.shape[:2], -100, dtype=torch.long)
    for b, (S, n) in enumerate(zip(sols_list, n_list)):
        St = torch.as_tensor(S)
        score = lp[b, torch.arange(n)[None], St].sum(1)
        tgt[b, :n] = St[int(score.argmax())]
    return tgt


def target_nearest(lg, sols_list, attempts):
    """A2: valid TRAINING solution with smallest Hamming distance to the failed attempt;
    ties -> higher model log-prob -> lowest index."""
    lp = torch.log_softmax(lg.detach(), -1)
    tgt = torch.full(lg.shape[:2], -100, dtype=torch.long)
    for b, (S, a) in enumerate(zip(sols_list, attempts)):
        n = len(a); St = torch.as_tensor(S)
        ham = (St != torch.as_tensor(a)[None]).sum(1).float()
        score = lp[b, torch.arange(n)[None], St].sum(1)
        key = ham * 1e4 - score                      # Hamming first, then likelihood
        tgt[b, :n] = St[int(key.argmin())]
    return tgt


class Control:
    """Best-checkpoint / plateau / instability / wall-time bookkeeping shared by all stages.
    sign=+1: higher metric is better (A, B); sign=-1: lower is better (C, Brier)."""

    def __init__(self, stage, m0, sign, min_delta, t0, eval_s):
        self.stage, self.sign, self.min_delta, self.t0 = stage, sign, min_delta, t0
        self.best, self.best_step, self.ref, self.since = m0, 0, m0, 0
        self.eval_s, self.losses = eval_s, []

    def time_up_soon(self, step_s):
        return time.time() - self.t0 + 1.2 * self.eval_s + 2 * step_s >= WALL[self.stage]

    def measure(self, step, m, loss, eval_s):
        """Returns (is_new_best, stop_reason or None)."""
        self.eval_s = max(self.eval_s, eval_s)
        new_best = self.sign * (m - self.best) > 0
        if new_best:
            self.best, self.best_step = m, step
        if self.sign * (m - self.ref) > self.min_delta:
            self.ref, self.since = m, 0
        else:
            self.since += 1
        reason = None
        if loss is not None:
            self.losses.append(loss)
            lmin = min(self.losses)
            if len(self.losses) >= 3 and all(x > 3 * lmin for x in self.losses[-3:]):
                reason = 'INSTABLE_LOSS_ABOVE_3X_MIN'
        if reason is None and self.since >= PATIENCE:
            reason = 'PLATEAU_NO_DEV_PROGRESS'
        return new_best, reason


def ce(lg, tgt):
    return F.cross_entropy(lg.reshape(-1, M.NV), tgt.reshape(-1), ignore_index=-100)


def dev_metric(stage, net, dev, dstat):
    net.eval()
    if stage == 'A':
        _, ok = cog.verify(dev, cog.decode(net, dstat))
        m = class_mean(ok, dev)
    elif stage == 'B':
        s, _ = cog.success_at_k(net, dev, dstat, 'FB', seed=12345)
        m = class_mean(s, dev)
    net.train()
    return m


def main():
    data, run, seed, stage = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    init = sys.argv[5] if len(sys.argv) > 5 else None
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    torch.set_num_threads(int(__import__("os").environ.get("P2_THREADS", "8")))
    t_start = time.time()
    run.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((data / 'manifest.json').read_text())
    train = D.load(data / 'train.jsonl'); dev = D.load(data / 'dev.jsonl')
    tp, ts = [p for p, _ in train], [s for _, s in train]
    tstat = [M.encode_static(p) for p in tp]
    dp = [p for p, _ in dev]; dstat = [M.encode_static(p) for p in dp]
    net = M.Net()
    if init:
        net.load_state_dict(torch.load(init, weights_only=True))
    if stage == 'C':
        for name, prm in net.named_parameters():
            prm.requires_grad = name.startswith('head_')
        return stage_c(net, run, seed, rng, tp, ts, tstat, dp, dev, dstat, manifest, init, data, t_start)
    opt = torch.optim.AdamW([q for q in net.parameters() if q.requires_grad], lr=LR[stage], weight_decay=0.01)
    meta = {'stage': stage, 'seed': seed, 'init': init, 'init_sha256': M.weights_sha256(net),
            'data_manifest_sha256': hashlib.sha256((data / 'manifest.json').read_bytes()).hexdigest(),
            'code_sha256': code_hash(), 'lr': LR[stage], 'batch': BATCH, 'eval_every': EVAL_EVERY,
            'patience': PATIENCE, 'min_delta': MIN_DELTA, 'wall_s': WALL[stage], 'torch': torch.__version__}
    log = open(run / 'log.jsonl', 'w')
    log.write(json.dumps({'event': 'start', **meta}) + '\n'); log.flush()
    t0 = t_start                                     # wall clock includes data loading and the step-0 measurement
    te = time.time(); m0 = dev_metric(stage, net, dp, dstat); eval_s = time.time() - te
    log.write(json.dumps({'event': 'eval', 'step': 0, 'dev': m0, 'weights_sha256': meta['init_sha256'],
                          'elapsed_s': round(time.time() - t0)}) + '\n')
    ctl = Control(stage, m0, +1, MIN_DELTA, t0, eval_s)
    step = 0
    torch.save(net.state_dict(), run / 'best.pt')
    losses, reason = [], None
    gen = torch.Generator().manual_seed(seed + 99)
    ts_step = time.time(); step_s = 0.0
    while reason is None:
        step += 1
        idx = rng.integers(0, len(tp), BATCH)
        bst = [tstat[i] for i in idx]; bsol = [ts[i] for i in idx]
        lg, _, _ = net.logits(M.collate(bst))
        loss = ce(lg, target_most_likely(lg, bsol, [tp[i].n for i in idx]))
        if stage == 'B':
            # on-policy failed attempts of the CURRENT model (greedy or tau=1 sample), optionally one repair deeper
            idx2 = rng.integers(0, len(tp), BATCH)
            p2 = [tp[i] for i in idx2]; s2 = [tstat[i] for i in idx2]; sol2 = [ts[i] for i in idx2]
            net.eval()
            a = cog.decode(net, s2, sample=bool(rng.random() < .5), gen=gen)
            fl, _ = cog.verify(p2, a)
            if rng.random() < .5:
                a = cog.decode(net, s2, M.MODE_FB, prev=a, flags=fl, sample=True, gen=gen)
                fl, _ = cog.verify(p2, a)
            net.train()
            mode = M.MODE_PREV if rng.random() < 1 / 3 else M.MODE_FB
            lg2, _, _ = net.logits(M.collate(s2, a, fl, mode))
            loss = 0.5 * loss + ce(lg2, target_nearest(lg2, sol2, a))
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0)
        opt.step()
        losses.append(float(loss))
        if not math.isfinite(losses[-1]):
            reason = 'INSTABLE_NONFINITE_LOSS'
            break
        now = time.time(); step_s = 0.9 * step_s + 0.1 * (now - ts_step) if step > 1 else now - ts_step; ts_step = now
        time_up = ctl.time_up_soon(step_s)
        if step % EVAL_EVERY == 0 or time_up:
            ml = float(np.mean(losses[-EVAL_EVERY:]))
            te = time.time(); m = dev_metric(stage, net, dp, dstat); eval_s = time.time() - te
            wsha = M.weights_sha256(net)
            rec = {'event': 'eval', 'step': step, 'dev': m, 'train_loss': ml, 'weights_sha256': wsha,
                   'elapsed_s': round(time.time() - t0), 'eval_s': round(eval_s, 1)}
            new_best, reason = ctl.measure(step, m, ml, eval_s)
            if new_best:
                torch.save(net.state_dict(), run / 'best.pt'); rec['best'] = True
            if (step // EVAL_EVERY) % KEEP_EVERY == 0 and step % EVAL_EVERY == 0:
                torch.save(net.state_dict(), run / f'step_{step}.pt')
            log.write(json.dumps(rec) + '\n'); log.flush()
            if reason is None and time_up:
                reason = 'WALL_TIME_LIMIT'
            ts_step = time.time()
    torch.save(net.state_dict(), run / 'last.pt')
    net.load_state_dict(torch.load(run / 'best.pt', weights_only=True))
    best_sha = M.weights_sha256(net)
    best, best_step = ctl.best, ctl.best_step
    end = {'event': 'end', 'reason': reason, 'steps': step, 'best_dev': best, 'best_step': best_step,
           'best_weights_sha256': best_sha, 'dev_untrained_or_init': m0, 'elapsed_s': round(time.time() - t0)}
    log.write(json.dumps(end) + '\n'); log.close()
    print(json.dumps(end), flush=True)


def stage_c(net, run, seed, rng, tp, ts, tstat, dp, dev, dstat, manifest, init, data, t_start):
    """A4: labels from TRAIN rollouts of the frozen stage-B model; heads trained, trunk frozen.
    p-label: greedy fresh a1 correct?  q-labels (only if a1 wrong): one rollout of each fixed 3-round strategy."""
    t0 = t_start; net.eval()                          # wall clock includes data loading and label rollouts
    log = open(run / 'log.jsonl', 'w')
    log.write(json.dumps({'event': 'start', 'stage': 'C', 'seed': seed, 'init': init,
                          'init_sha256': M.weights_sha256(net), 'code_sha256': code_hash(),
                          'data_manifest_sha256': hashlib.sha256((data / 'manifest.json').read_bytes()).hexdigest(),
                          'lr': LR['C'], 'batch': BATCH, 'eval_every': EVAL_EVERY, 'patience': PATIENCE,
                          'min_delta': MIN_DELTA_C, 'wall_s': WALL['C'], 'torch': torch.__version__}) + '\n')

    def states(problems, statics, n_max, rs):
        sel = rs.permutation(len(problems))[:n_max]
        ps = [problems[i] for i in sel]; ss = [statics[i] for i in sel]
        a1 = []; [a1.extend(cog.decode(net, ss[c])) for c in cog.chunks(len(ss))]
        fl, ok = cog.verify(ps, a1)
        wrong = np.nonzero(~ok)[0]
        pw = [ps[i] for i in wrong]; sw = [ss[i] for i in wrong]
        aw = [a1[i] for i in wrong]; fw = [fl[i] for i in wrong]
        qr, _ = cog.strategy_rollout(net, pw, sw, aw, fw, 'rep', seed=seed + 1)
        qn, _ = cog.strategy_rollout(net, pw, sw, aw, fw, 'new', seed=seed + 2)
        return ps, ss, a1, fl, ok, wrong, qr, qn

    rs = np.random.default_rng(seed + 5)
    tr = states(tp, tstat, 40000, rs)
    dv = states(dp, dstat, len(dp), np.random.default_rng(seed + 6))
    log.write(json.dumps({'event': 'labels', 'train_states': len(tr[0]), 'train_a1_correct': float(tr[4].mean()),
                          'train_wrong': len(tr[5]), 'train_q_rep': float(tr[6].mean()) if len(tr[5]) else None,
                          'train_q_new': float(tr[7].mean()) if len(tr[5]) else None,
                          'dev_a1_correct': float(dv[4].mean()), 'elapsed_s': round(time.time() - t0)}) + '\n')
    log.flush()
    opt = torch.optim.AdamW([q for q in net.parameters() if q.requires_grad], lr=LR['C'])

    def batches_p(S, idx):
        ps, ss, a1, fl, ok = S[:5]
        b = M.collate([ss[i] for i in idx], [a1[i] for i in idx], None, M.MODE_PREV)
        return b, torch.as_tensor(ok[idx], dtype=torch.float)

    def batches_q(S, j):
        ps, ss, a1, fl, ok, wrong, qr, qn = S
        idx = wrong[j]
        b = M.collate([ss[i] for i in idx], [a1[i] for i in idx], [fl[i] for i in idx], M.MODE_FB)
        return b, torch.as_tensor(np.stack([qr[j], qn[j]], 1), dtype=torch.float)

    def dev_brier():
        with torch.no_grad():
            bp = []; bq = []
            for c in cog.chunks(len(dv[0])):
                b, y = batches_p(dv, np.arange(c.start, c.stop))
                pl, _ = net.heads(b); bp.append(((torch.sigmoid(pl) - y) ** 2).numpy())
            for c in cog.chunks(len(dv[5])):
                b, y = batches_q(dv, np.arange(c.start, c.stop))
                _, ql = net.heads(b); bq.append(((torch.sigmoid(ql) - y) ** 2).mean(1).numpy())
            return float(np.mean([np.concatenate(bp).mean(), np.concatenate(bq).mean() if bq else 0.0]))

    te = time.time(); b0 = dev_brier(); eval_s = time.time() - te
    step, reason = 0, None
    ctl = Control('C', b0, -1, MIN_DELTA_C, t0, eval_s)
    log.write(json.dumps({'event': 'eval', 'step': 0, 'dev_brier': b0, 'elapsed_s': round(time.time() - t0)}) + '\n')
    torch.save(net.state_dict(), run / 'best.pt')
    gw = len(tr[5]); losses = []
    ts_step = time.time(); step_s = 0.0
    while reason is None:
        step += 1
        ip = rng.integers(0, len(tr[0]), BATCH)
        b, y = batches_p(tr, ip); pl, _ = net.heads(b)
        loss = F.binary_cross_entropy_with_logits(pl, y)
        if gw:
            b, y = batches_q(tr, rng.integers(0, gw, BATCH)); _, ql = net.heads(b)
            loss = loss + F.binary_cross_entropy_with_logits(ql, y)
        opt.zero_grad(); loss.backward(); opt.step()
        losses.append(float(loss.detach()))
        now = time.time(); step_s = 0.9 * step_s + 0.1 * (now - ts_step) if step > 1 else now - ts_step; ts_step = now
        time_up = ctl.time_up_soon(step_s)
        if not math.isfinite(losses[-1]):
            reason = 'INSTABLE_NONFINITE_LOSS'
        elif step % EVAL_EVERY == 0 or time_up:
            te = time.time(); m = dev_brier(); eval_s = time.time() - te
            ml = float(np.mean(losses[-EVAL_EVERY:]))
            rec = {'event': 'eval', 'step': step, 'dev_brier': m, 'train_loss': ml,
                   'weights_sha256': M.weights_sha256(net), 'elapsed_s': round(time.time() - t0)}
            new_best, reason = ctl.measure(step, m, ml, eval_s)
            if new_best:
                torch.save(net.state_dict(), run / 'best.pt'); rec['best'] = True
            log.write(json.dumps(rec) + '\n'); log.flush()
            if reason is None and time_up:
                reason = 'WALL_TIME_LIMIT'
            ts_step = time.time()
    torch.save(net.state_dict(), run / 'last.pt')
    net.load_state_dict(torch.load(run / 'best.pt', weights_only=True))
    end = {'event': 'end', 'reason': reason, 'steps': step, 'best_dev_brier': ctl.best, 'best_step': ctl.best_step,
           'best_weights_sha256': M.weights_sha256(net), 'dev_brier_init': b0, 'elapsed_s': round(time.time() - t0)}
    log.write(json.dumps(end) + '\n'); log.close()
    print(json.dumps(end), flush=True)


if __name__ == '__main__':
    main()
