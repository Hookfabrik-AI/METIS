#!/usr/bin/env python3
"""Recompute, and verify against registered, selected four-arm Qwen results."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[1]

def summarize():
    idx=json.loads((ROOT/'evidence/index.json').read_text())
    sel=idx['selection']
    recs=[]
    for task in sorted(sel):
        run=sel[task]
        data=json.loads((ROOT/f'evidence/qwen/run_{run:02}/results.json').read_text())
        matches=[r for r in data if r['id']==task]
        if len(matches)!=1:raise ValueError(f'{task}: expected one record in run_{run:02}')
        recs.append(matches[0])
    output={}
    for arm in 'ABCD':
        rows=[row[arm] for row in recs]
        output[arm]={
            'correct':sum(int(a['solved']) for a in rows),
            'tasks':len(rows),
            'output_tokens':sum(a['qwen_output_tokens'] for a in rows),
            'qwen_wall_s':round(sum(a['qwen_wall_s'] for a in rows),1),
            'attempts':sum(a['attempts_used'] for a in rows),
            'candidate_correct_posthoc':None if arm=='A' else sum(int(a['proposal']['correct_posthoc']) for a in rows),
            'proposal_cpu_s_sum':None if arm=='A' else round(sum(a['proposal']['cpu_s'] for a in rows),5)
        }
    expected=idx['qwen_four_arm']['statistics']
    if output!=expected:
        print('ERROR: reconstructed values differ from registered index',file=sys.stderr)
        print(json.dumps({'actual':output,'expected':expected},indent=2),file=sys.stderr)
        return False
    print('Qwen four-arm: evidence index VERIFIED against selected raw results')
    for arm,stats in output.items():
        print(f'{arm}  {stats["correct"]}/{stats["tasks"]}  output tokens={stats["output_tokens"]:,}  Qwen wall={stats["qwen_wall_s"]:,.1f}s')
    print('Selection:',', '.join(f'{t}=run_{sel[t]:02}' for t in sorted(sel)))
    return True
if __name__=='__main__':sys.exit(0 if summarize() else 1)
