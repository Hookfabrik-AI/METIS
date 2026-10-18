#!/usr/bin/env bash
# Portable reconstruction of the P2 training chain.
# CPU-heavy; not executed as part of the repository integrity check.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/research/p2"
PY="${METIS_PYTHON:-python3}"
DATA="$ROOT/datasets/p2"
RUNS="${METIS_RUNS_DIR:-$ROOT/runs/p2}"
mkdir -p "$RUNS"
for s in 0 1 2; do
  P2_THREADS=8 "$PY" -I -B train.py "$DATA" "$RUNS/seed$s/A" "$s" A
  P2_THREADS=8 "$PY" -I -B train.py "$DATA" "$RUNS/seed$s/B" "$s" B "$RUNS/seed$s/A/best.pt"
  if [[ "$s" == 0 ]]; then
    P2_THREADS=8 "$PY" -I -B train.py "$DATA" "$RUNS/seed0/C" 0 C "$RUNS/seed0/B/best.pt"
  fi
done
printf '%s\n' 'P2_TRAINING_CHAIN_DONE'
