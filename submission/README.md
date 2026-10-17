# Submission

This folder will hold the Codabench submission: `submission.py`, which defines
`class Solver(CompetSolver)`, plus its weight files. It stays a thin wrapper
around code in `src/`.

Contract (from the kit's `benchmark_utils/base_solver.py` and
`tracks/bci_decoding/objective.py`):
- `load_model(meta)` (required) returns a model exposing `predict(X)`, where
  `X` is a torch tensor `(B, C, T)` and the result has shape `(B,)` of int
  classes `{0: motor imagery, 1: mental subtraction, 2: word generation}`.
- `fit(model, train_loader)` (optional) runs only locally with `training=True`.
  Codabench is inference-only.
- `save_model(model, path)` (optional) writes the weights that `load_model`
  reads from `meta["submission_dir"]`.
- Optional `reset_state()` on the model is called on a fresh `deepcopy` before
  each subject x session stream.

Packaged ZIPs (`*.zip`) are git-ignored.
