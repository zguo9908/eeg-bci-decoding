# T1 · Evaluation: official metric, chance level, local streamed evaluation

## Why
Every later modelling decision is judged with this code, so it must
reproduce the official score exactly and say how large differences must be
before they mean anything (~95 trials per cell; the published baselines are
32.6–36% against 33.3% chance).

## Facts to rely on (read first)
- Metric: `external/2026-competition/tracks/bci_decoding/objective.py`
  (`evaluate_result`) and `external/2026-competition/benchmark_utils/metrics.py`
  (`balanced_accuracy`, `group_scores`). Balanced accuracy is computed per
  subject × session × context (interface) cell, then averaged over cells.
- Streaming: `external/2026-competition/benchmark_utils/streaming.py`
  (`predict_streams`: B = 1, recording order, deep-copied model plus
  `reset_state()` per stream). `benchmark_utils/data.py::make_loader` builds
  a contract-conforming loader from arrays.
- Cell structure: `src/bids_metadata.py::cue_trials` gives per-cell class
  counts from BIDS metadata, with no EEG needed.

## Owns
- `src/evaluation.py` (new)
- `tests/test_evaluation.py` (new)

## Part A (can start now)
1. `cell_balanced_accuracy(y_true, y_pred, cells) -> (mean, per_cell)`:
   our own implementation, so the metric is understood rather than imported.
   Read how the kit handles edge cases (a class absent from a cell, a
   prediction of a class never seen in the cell) and mirror them; document
   each one as a fact citing the line.
2. Test it against hand-computed small cases, **and** against the kit's own
   `group_scores(balanced_accuracy, ...)` on randomized inputs. Import the kit
   in tests via `sys.path` (as `src/splits.py` does), never by copying it.
3. Chance distribution of the cell-mean score for a predictor that ignores the
   EEG. Implement the permutation null that keeps each cell's predicted
   label counts (shuffle predictions within cells). In the report, explain at
   least one alternative null (e.g. uniform random guessing) and when it
   would differ. Test that its mean is ≈ 1/3 and that its spread shrinks
   with more cells.
4. Report the 95% chance interval for (a) the official test cell structure
   (8 cells; counts from BIDS metadata only, no EEG or predictions of test
   subjects) and (b) the validation structure (P05, P08: 4 cells). Then read
   the published baselines against it.

## Part B (after T0's `src/data.py` exists)
5. `evaluate_streamed(model, X, y, meta)`: wrap arrays with the kit's
   `make_loader` (stream_id = subject × session, context_id = interface,
   record_id = run, acquisition order), call the kit's `predict_streams`,
   and score with Part A. Call `assert_no_test_subjects` on `meta.subject`.
6. Integration test: a constant model scores exactly the value Part A
   predicts. A deliberately stateful dummy model shows that state does not
   cross sessions (it resets).

## Assumptions to state in docstrings
Trials are treated as exchangeable within a cell for the null; cells are
independent under the null (not true for a real model that shares
parameters across cells; say why that matters).

## Escalate
- Any choice of validation scheme (that is decision D1 in `docs/tasks/README.md`;
  provide the numbers that inform it, do not choose).

## Report back
API, edge-case facts with citations, test results, the chance intervals
(a) and (b), proposed edits to shared files, and the commit command.
