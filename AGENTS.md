# Instructions for AI agents working in this repository

The goal is understanding and a reproducible, rigorous pipeline, **not**
leaderboard score.

## Working rules
1. Explain the relevant code before changing it.
2. Make small, testable changes; never generate a whole pipeline at once.
3. For every implementation, state its signal-processing / ML assumptions.
4. Label claims as **fact** (cite the source file or page), **assumption**,
   or **recommendation**.
5. Before any modeling decision (features, model, normalization,
   adaptation, hyperparameter search), present alternatives and let the
   human choose.
6. Write unit tests for preprocessing and evaluation functions.
7. Do not modify or delete unrelated files without explaining why.

## Evaluation invariants (never break)
- The official public split is NeuralBench `SklearnSplit` by subject,
  60/20/20, `random_state=33` (fixed in the NeuralBench 0.4.0
  `_motor_imagery_stream` config, independent of benchopt's `seed`).
- **Test-split subjects are never used** for training, normalization
  statistics, feature selection, hyperparameter choice, or model selection.
  The warm-up test labels are public, so the only safeguard is our code.
- Model selection uses train/validation subjects only.
- Evaluation mirrors the official contract: one window at a time (`B = 1`)
  in recording order, a fresh model copy per subject x session stream, no
  labels at inference, and no state crossing sessions.
- The ranking metric is balanced accuracy per subject x session x interface
  (Graz / BrainHero) cell, averaged over cells.
- The official kit (`2026-competition`) is read-only: never edit its
  objective, metrics, or streaming code.

## Sources of truth
- Kit: https://github.com/neural-interfaces26/2026-competition
  (`tracks/bci_decoding/`, `codabench/pages/scientific_faq_bci.md`)
- Data: PROTEUS, NEMAR `nm000290` (BIDS, CC BY 4.0)
