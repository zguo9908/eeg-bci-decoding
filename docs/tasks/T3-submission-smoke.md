# T3 · Submission smoke test (urgent)

## Why
Sealed-phase execution logs are hidden and the sealed phase allows only
**5 submissions in total** (`external/2026-competition/codabench/pages/terms.md`).
The warm-up phase, which still shows logs, closes **Sun Nov 1, 23:59 CET**.
Goal: prove our build → validate → ZIP path works end to end with a trivial
model, and get the human a ZIP to upload to warm-up before it closes. This is a
pipeline check; the score itself is meaningless (expected ≈ 33.3%).

## Facts to rely on (read these files first)
- Contract: `external/2026-competition/codabench/pages/participate.md`
  (sections "Submission rules", "The submission.py contract",
  "Test your submission locally", "Common submission errors").
- Base class: `external/2026-competition/benchmark_utils/base_solver.py`.
- Reference: `external/2026-competition/solution/bci_decoding/submission.py`
  and `tracks/bci_decoding/solvers/constant.py`.
- One self-contained `submission.py` at the ZIP root plus its weight files;
  no extra Python modules; only packages in the kit's `requirements.txt`.
- The env is `~/miniforge3/envs/eeg-bci` (already has benchopt and the kit
  stack). Real data is prepared under `data/benchopt`; benchopt finds it when
  `BENCHOPT_DATA_HOME="$PWD/data/benchopt"` is set (see `scripts/prepare_data.sh`).

## Owns
- `submission/smoke_constant/submission.py` (new)
- `scripts/package_submission.sh` (new)
- `submission/README.md` (may extend with the validated procedure)

## Steps
1. Write `submission/smoke_constant/submission.py`: a constant-class model
   (adapt the kit's Constant solver). Explain in the docstring why a constant
   model is the right smoke test (no learned parameters, known score).
2. Local check A, contract on synthetic data (no download):
   `COMPET_SUBMISSION_DIR=$PWD/submission/smoke_constant benchopt run external/2026-competition/tracks/bci_decoding -d Simulated -s $PWD/submission/smoke_constant/submission.py`
   Use the existing env; do not let benchopt create a new conda env. If
   benchopt insists on installing, report the exact message instead of working
   around it with flags you have not verified.
3. Local check B, real PROTEUS data, inference-only, same command with
   `-d "BCI[study=dreyer2026proteus]"` and `BENCHOPT_DATA_HOME` set. Expect
   `balanced_accuracy_cell_mean` ≈ 0.333 and `n_cells` = 8.
   Note: this evaluates on the official **test** subjects (P04, P09). That is
   acceptable only because the model has no learned parameters; never iterate
   on this number.
4. `scripts/package_submission.sh <submission_dir>`: zip the folder's files
   **flat at the ZIP root** (`zip -j`) into `submission/<name>.zip`
   (git-ignored), then list the ZIP contents and fail if `submission.py` is not
   at the root or if any `__pycache__`/`.pyc` sneaks in.
5. Produce `submission/smoke_constant.zip` and hand it to the human with
   upload instructions: Codabench Track 02 → My Submissions → phase
   **"Warm-up Phase (update 1)"**. Do **not** upload anything yourself.

## Acceptance criteria
- Both local checks run, and their outputs (metric lines) are quoted in the report.
- The ZIP passes the script's own checks; its listing is shown.
- `submission.py` imports only `benchmark_utils.*`, numpy and torch.

## Escalate (ask the human, do not decide)
- Anything requiring changes to the kit or installing new packages.
- **D6 packaging strategy**: real models will live in `src/`, but the platform
  accepts one file. Describe 2-3 options (e.g. keep model code self-contained
  in `submission/<model>/submission.py` and have `src/` import from it; or a
  build script that inlines code; or something else), with trade-offs for
  testability and the reproducibility audit. Do not implement one.

## Report back
Commands run and their key output, the ZIP path and listing, any surprises
in the contract, proposed edits to shared files, and the commit command for
the owned files.
