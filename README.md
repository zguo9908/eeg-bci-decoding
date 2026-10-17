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
conda env create -f environment.yml
conda activate eeg-bci
pip freeze > requirements-lock.txt   # record resolved versions
pytest
```

## Status
- [x] Scaffold
- [x] Data exploration: BIDS metadata (subjects, sessions, runs, events) — `src/bids_metadata.py`,
      `notebooks/01_bids_metadata.ipynb`
- [ ] Reproduce the official split and audit it
