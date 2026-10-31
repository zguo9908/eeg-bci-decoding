# EEG/BCI decoding — Neural Interfaces 2026, Track 2

A learning-oriented, reproducible pipeline for three-class mental-command
decoding (kinesthetic motor imagery, mental subtraction, word generation) from
41-channel EEG on the PROTEUS dataset (NEMAR `nm000290`).

The focus is scientific rigor and understanding, not leaderboard score. See
[AGENTS.md](AGENTS.md) for working rules and the evaluation invariants.

## Task in one paragraph
Input: 4 s windows (cue + 1 s to cue + 5 s), 41 EEG channels, notch 50/60 Hz,
band-pass 0.1–75 Hz, resampled to 120 Hz, in µV → shape `(1, 41, 480)`.
Output: one class index per window. Windows are streamed one at a time per
subject x session, and each session starts from a fresh model copy.
Metric: balanced accuracy per subject x session x interface cell, averaged
over cells. The sealed phase tests later sessions of known participants
**and** new participants.

## Layout
```
src/            library code (preprocessing, features, models, evaluation)
tests/          pytest unit tests
notebooks/      exploration; they import from src/ and keep no core logic
configs/        experiment configs
experiments/    experiment records (runs/ is git-ignored)
reports/        write-ups and figures
submission/     Codabench Solver wrapper (see submission/README.md)
data/           local data (git-ignored)
```

## Setup
```bash
git clone --recursive https://github.com/zguo9908/eeg-bci-decoding.git
# (already cloned without --recursive?  git submodule update --init)
conda env create -f environment.yml
conda activate eeg-bci
scripts/prepare_data.sh               # ~1.6 GB download, 2.3 GB on disk, into data/
pytest -m "not integration"           # fast unit tests
pytest -m integration                 # checks against the official kit + data
```

The official competition kit is a git submodule at `external/2026-competition`,
pinned to commit `a66bc23` and never edited. `requirements-lock.txt` records the
resolved package versions.

## Official public split (fact, read from the kit)
| split | subjects | windows |
|---|---|---|
| train | P01, P02, P03, P06, P07, P10 (3 sessions) | 1521 |
| val   | P05, P08 | 379 |
| test  | P04 (3 sessions), P09 | 755 |

`src.splits.assert_no_test_subjects` must guard every development step.

## Status
- [x] Scaffold
- [x] Data exploration: BIDS metadata (subjects, sessions, runs, events) — `src/bids_metadata.py`,
      `notebooks/01_bids_metadata.ipynb`
- [x] Official kit as pinned submodule; data prepared through it (`scripts/prepare_data.sh`)
- [x] Reproduce the official split and audit it — `src/splits.py`
