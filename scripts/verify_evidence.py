#!/usr/bin/env python3
"""Verify content hashes and dataset lineage in the prepared research archive.

This does not validate original experiments, only curated artifact integrity.
"""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def verify():
    provenance=json.loads((ROOT/'evidence/provenance.json').read_text())
    missing=[];mismatch=[]
    for ent in provenance['items']:
        path=ROOT/ent['repo_path']
        if not path.is_file():missing.append(ent['repo_path'])
        elif sha(path)!=ent['repo_sha256']:mismatch.append(ent['repo_path'])
    manifest=json.loads((ROOT/'datasets/p2/manifest.json').read_text())
    for split,meta in manifest['splits'].items():
        path=ROOT/'datasets/p2'/f'{split}.jsonl'
        if not path.is_file():missing.append(str(path.relative_to(ROOT)))
        elif sha(path)!=meta['sha256']:mismatch.append(str(path.relative_to(ROOT)))
    src=ROOT/'research/p2/problems.py'
    if sha(src)!=manifest['problems_sha256']:mismatch.append(str(src.relative_to(ROOT)))
    total=len(provenance['items'])
    print(f'Files checked: {total}; P2 splits: {len(manifest["splits"])}')
    print(f'Files missing: {len(missing)}, hash mismatches: {len(mismatch)}')
    if missing: print('MISSING', *missing, sep='\n  ')
    if mismatch: print('MISMATCH', *mismatch, sep='\n  ')
    return not (missing or mismatch)
if __name__=='__main__':sys.exit(0 if verify() else 1)
