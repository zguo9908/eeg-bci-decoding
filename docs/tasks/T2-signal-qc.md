# T2 · Signal quality notebook (train subjects only)

## Why
Before choosing features or models, know what the signal looks like:
bad channels, amplitude scale differences across subjects and sessions (the
main obstacle to cross-subject transfer), and whether class-related spectral
differences exist in the task-only half vs. the feedback half of the window.

## Facts to rely on
- Notebook 01 (`notebooks/01_bids_metadata.ipynb`) established that feedback
  starts at cue + 3.0 s, so the official window (cue + 1 → 5 s) is samples
  0–239 task-only and 240–479 during feedback (120 Hz). On BrainHero, feedback
  onset jitters about ±50 ms; on Graz it is exact.
- Calibration runs have sham feedback; online runs have real feedback.
- Input is µV after the official filters (notch 50/60 Hz, band-pass 0.1–75 Hz).
- Data access: `src/data.py::load_windows` (from T0). Use **train subjects
  only** (`src.splits.subjects_in("train")`). Validation subjects are for
  model selection: do not look at their class-wise statistics here.

## Owns
- `src/qc.py` (new): pure functions such as robust per-channel amplitude,
  flat/noisy channel flags, Welch band power.
- `tests/test_qc.py` (new): unit tests on synthetic signals with known
  answers (a sine at a known frequency, a flat channel, a channel with
  added noise).
- `notebooks/02_signal_qc.ipynb` (new): calls `src/qc.py` and plots only;
  saved with outputs.

## Notebook sections
1. Amplitude: robust per-channel scale by subject × session × run. Flag
   flat or extreme channels (state the thresholds and why).
2. Scale shift across subjects and sessions (P10 has 3 sessions): how much do
   per-subject channel scales differ? This motivates (does not choose) any
   normalization.
3. Spectra: Welch PSD averaged per class, per interface, and per mode. State
   the Welch parameters and the frequency resolution they give with 2 s halves
   at 120 Hz.
4. Task-only vs. feedback half: class-wise band power (theta, alpha/mu, beta)
   over sensorimotor vs. other channels, separately for each half. This is
   **descriptive only**: no classifier, no statistical claims beyond what the
   plots show.
5. Summary labelled fact / assumption / recommendation.

For plots, follow notebook 01's style block (same neutral colours; class
colours mi #2a78d6, sub #eb6834, word #1baf7a).

## Escalate
- Excluding channels, trials or runs from later analyses.
- Any normalization or re-referencing for modelling.
- Any statistical test you want to add beyond description.

## Report back
Key findings with their labels, figures you would highlight, proposed
decisions for the human (not taken), proposed edits to shared files, and the
commit command.
