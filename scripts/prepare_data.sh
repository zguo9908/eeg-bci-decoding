#!/usr/bin/env bash
# Download PROTEUS and build the official preprocessed windows through the
# pinned competition kit (external/2026-competition), unchanged.
#
# BENCHOPT_DATA_HOME overrides benchopt's default data location (inside the
# kit), so the data lives in this repo's git-ignored data/ folder and survives
# submodule updates. Idempotent: re-running reuses the cache.
#
# Usage: conda activate eeg-bci && scripts/prepare_data.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TRACK="$ROOT/external/2026-competition/tracks/bci_decoding"

export BENCHOPT_DATA_HOME="$ROOT/data/benchopt"
mkdir -p "$BENCHOPT_DATA_HOME"

benchopt prepare "$TRACK" --config "$TRACK/training.yml"
