# T0 · Data access layer for development subjects

## Why
T1 (local evaluation) and T2 (signal QC) both need the official preprocessed
windows as arrays together with per-window metadata. Building this once, with
the leakage guard inside, prevents two conversations from writing competing
loaders and makes it impossible to load test subjects by accident.

## Facts to rely on
- The official windows come from the kit's NeuralBench pipeline:
  `external/2026-competition/tracks/bci_decoding/benchmark_utils/nb_task.py`
  (`load_task`, `_NBWindows`) and `datasets/bci_studies.py` (`_load`: the
  `target_transform`, `context_of`, `order_of` it passes). Windows are
  (41, 480): 4 s at 120 Hz, in µV, notch 50/60 Hz + band-pass 0.1–75 Hz
  (zero-phase, applied offline before streaming).
- `src/splits.py::official_split_from_kit` already shows how to reach the
  segments: `loaders[split].loader.dataset` is an `_NBWindows`; its
  `seg_ds.segments[i].trigger.to_dict()` holds `subject`
  ("Dreyer2026Proteus/P01"), `session`, `task`, `run`, `description`
  (mi/sub/word), `code`. `_NBWindows.index` gives the order its
  `__getitem__` reads. The train loader shuffles, so read the dataset, not
  the DataLoader.
- `load_task` always builds a test loader and reads one test window to infer
  shapes. That single read is unavoidable without editing the kit (forbidden);
  it is never returned. State this in the docstring.
- Official subjects per split: `src/splits.py`. Class ids: 0 = mi,
  1 = sub, 2 = word (`src/bids_metadata.CLASSES`, `scientific_faq_bci.md`).
- Prepared data: `data/benchopt/neural_compet` (from `scripts/prepare_data.sh`).

## Owns
- `src/data.py` (new)
- `tests/test_data.py` (new)

## Goal
`load_windows(subjects, data_dir) -> (X, y, meta)`:
- Calls `assert_no_test_subjects(subjects)` **before** touching any data.
- `X`: float32 `(N, 41, 480)`; `y`: int64 `(N,)`; `meta`: DataFrame with
  `subject, session, run, task, interface, mode, onset, label`, and
  `stream_id` (one per subject × session) for use with the kit's streaming
  evaluator.
- Rows sorted in acquisition order: subject, session, run, onset.
- Reuse `src.bids_metadata.INTERFACES` and the mode rule (task name starts
  with "Online") rather than redefining them.
- Report how long a full load of the 8 development subjects takes. If it is
  over ~1 minute, **propose** an on-disk cache (key it on subjects, kit
  commit and neuralbench version), but do not build it without asking.

## Tests
Unit tests (fast, no data):
- Passing a test subject raises before any loading happens. Monkeypatch the
  kit loader to fail if called.
Integration tests (`@pytest.mark.integration`, skip if data missing):
- Shapes and dtypes; per-subject window counts equal those from
  `src.bids_metadata.cue_trials` for the same subjects.
- `y` equals `CLASSES.index(description)` for every window.
- Rows are in acquisition order, and `meta` agrees with the BIDS cue table on
  (subject, session, run, onset) to within one sample (1/120 s).
- Amplitudes are plausible for µV EEG. Report the values, and assert only on
  loose bounds, explained in a comment.

## Escalate
- Any change to preprocessing (filters, resampling, re-referencing,
  scaling): that is a modelling decision.
- Any need to change the kit.

## Report back
The API, the assumptions, test results, load time, the cache proposal if
needed, proposed edits to shared files (e.g. a README line), and the commit
command for the owned files.
