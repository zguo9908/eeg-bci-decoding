# Subtasks and coordination

Work is split into briefs that separate Claude Code conversations can run.
Each brief is self-contained: context, goal, the files it owns, steps,
acceptance criteria, and decisions it must hand back to the human.

## How to start a subtask
Open a new Claude Code conversation in this repository and paste:

> Read `AGENTS.md`, then `docs/tasks/<brief>.md`, and carry out that brief.

## Rules for every subtask conversation
- Edit **only the files listed under "Owns"** in your brief. Shared files
  (`README.md`, `AGENTS.md`, `pyproject.toml`, `environment.yml`,
  `docs/tasks/*`) belong to the coordinator: propose changes to them in your
  final report instead of making them.
- Do not commit. End with a `git add <owned files>` + `git commit` command the
  human can run, so parallel work never mixes in one commit.
- Never touch `external/2026-competition` (read-only official kit).
- Stop and ask the human at every item listed under "Escalate".
- Run unit tests with `~/miniforge3/envs/eeg-bci/bin/python -m pytest -m "not integration"`
  and the data-backed tests with `-m integration`.

## Status (2026-10-30)
Done: scaffold · BIDS metadata + notebook 01 · kit submodule · data prepared
(`scripts/prepare_data.sh`) · official split + leakage guard (`src/splits.py`).

| ID | Brief | Depends on | Can run in parallel with | Urgency |
|----|-------|-----------|--------------------------|---------|
| T3 | [Submission smoke test](T3-submission-smoke.md) | — | T0 | **Warm-up closes Sun Nov 1, 23:59 CET** |
| T0 | [Data access layer](T0-data-access.md) | — | T3 | blocks T1-B, T2 |
| T1 | [Evaluation metric, chance level, local streamed eval](T1-evaluation.md) | Part A: — · Part B: T0 | T2 | before any modelling |
| T2 | [Signal quality notebook](T2-signal-qc.md) | T0 | T1 | before any modelling |

```
T3 ─────────────────────────────► (ZIP validated on warm-up)
T0 ──┬──► T1 (part B) ──┐
     └──► T2 ───────────┴──► decisions D1–D3 below
T1 part A can start now.
```

## Backlog: needs the human's decision first (not relayable yet)
- **D1 Internal validation scheme** (after T1): official val only (2 subjects)
  vs. leave-one-subject-out over the 8 train+val subjects vs. LOSO plus a
  cross-session check on P10.
- **D2 First decoding baselines** (after D1, T2): e.g. CSP+LDA, Riemannian
  tangent space + logistic regression, EEGNet. Note: the worker image has no
  `pyriemann`, so Riemannian code must be implemented inside `submission.py`.
- **D3 Feedback confound**: does decoding rely on the feedback half of the
  window (cue+3–5 s)? Needs a model, so it follows D2.
- **D4 Within-session, label-free adaptation** (e.g. running re-centering of
  covariances). Allowed by the FAQ if causal and reset per session.
- **D5 Final-refit policy**: the sealed phase tests later sessions of all 10
  public participants, P04/P09 included. Refit the final model on all public
  subjects? If yes, add an explicit, logged override to the leakage guard for
  that step only.
- **D6 Submission packaging** (from T3): how model code from `src/` ends up in
  a single self-contained `submission.py`.
- **Audit pack** (by Nov 21): method description, training config, compute
  and data disclosures (`codabench/pages/terms.md`).
