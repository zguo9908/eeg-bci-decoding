"""Read the PROTEUS (NEMAR nm000290) BIDS metadata into tidy tables.

Only the small ``*_events.tsv`` sidecars are read; no EEG signal is loaded.
This answers structural questions before any modelling: who has how many
sessions and runs, how many trials per class in each subject x session x
interface cell, and where feedback starts relative to the cue.

Facts used here (dataset README and ``*_events.json``, nm000290):
- Cue onsets are the events with ``trial_type`` in {mi, sub, word}.
- Runs are named ``task-<Mode><Interface>``: Mode in {Acquisition, OnlineRaw}
  (calibration with sham feedback vs. online with real feedback); Interface
  in {Graz, BH (BrainHero)}. Baseline runs have no cues.
The task -> interface mapping mirrors the official kit
(``tracks/bci_decoding/datasets/bci_studies.py``, ``_PROTEUS_INTERFACES``).
"""

import json
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

# Release the official kit uses ("NEMAR nm000290 v1.0.0", bci_studies.py).
DATASET_REPO = "nemarDatasets/nm000290"
DATASET_REF = "v1.0.0"

CLASSES = ("mi", "sub", "word")  # index = official class id (0, 1, 2)

INTERFACES = {
    "AcquisitionBH": "BrainHero",
    "OnlineRawBH": "BrainHero",
    "AcquisitionGraz": "Graz",
    "OnlineRawGraz": "Graz",
}

_ENTITY = re.compile(r"(sub|ses|task|run)-([A-Za-z0-9]+)")


def fetch_metadata(dest, ref=DATASET_REF, repo=DATASET_REPO):
    """Download the dataset's ``.tsv`` / ``.json`` / ``.md`` files, no EEG.

    Files come from the GitHub mirror of the NEMAR release, pinned to ``ref``
    (a tag or commit), and keep their BIDS paths under ``dest``. Existing
    files are overwritten. Returns the number of files written.
    """
    api = f"https://api.github.com/repos/{repo}/git/trees/{ref}?recursive=1"
    with urllib.request.urlopen(api) as resp:
        tree = json.load(resp)
    if tree.get("truncated"):
        raise RuntimeError("GitHub tree listing truncated; files would be missed")
    paths = [item["path"] for item in tree["tree"]
             if item["type"] == "blob"
             and item["path"].endswith((".tsv", ".json", ".md"))
             and not item["path"].startswith(".")]
    dest = Path(dest)

    def get(path):
        target = dest / path
        target.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(
            f"https://raw.githubusercontent.com/{repo}/{ref}/{path}", target)

    with ThreadPoolExecutor(8) as pool:
        list(pool.map(get, paths))
    return len(paths)


def parse_entities(filename):
    """BIDS entities of a file name, e.g. ``{"sub": "P01", "ses": "1", ...}``.

    ``run`` is returned as an int; missing entities are absent from the dict.
    """
    entities = dict(_ENTITY.findall(Path(filename).name))
    if "run" in entities:
        entities["run"] = int(entities["run"])
    return entities


def load_events(root):
    """All ``*_events.tsv`` under ``root`` as one table, one row per event.

    Adds the file's ``subject``, ``session``, ``task`` and ``run`` columns.
    """
    tables = []
    for path in sorted(Path(root).rglob("*_events.tsv")):
        ent = parse_entities(path)
        df = pd.read_csv(path, sep="\t")
        df.insert(0, "subject", ent["sub"])
        df.insert(1, "session", ent["ses"])
        df.insert(2, "task", ent["task"])
        df.insert(3, "run", ent["run"])
        tables.append(df)
    if not tables:
        raise FileNotFoundError(f"No *_events.tsv under {root}")
    return pd.concat(tables, ignore_index=True)


def _next_onset_after(onsets, t, limit):
    """First onset in ``onsets`` with ``t < onset < limit``, else NaN."""
    later = onsets[(onsets > t) & (onsets < limit)]
    return later.min() if len(later) else float("nan")


def cue_trials(events):
    """One row per cued trial, with its label and within-trial timing.

    Columns: subject, session, task, run, interface, mode, onset, label,
    feedback_delay (start_feedback - cue, s), trial_end (end_trial - cue, s).
    A timing column is NaN if its event is missing before the next cue.
    Rows are sorted in acquisition order (subject, session, run, onset).
    """
    rows = []
    for (subject, session, task, run), run_ev in events.groupby(
            ["subject", "session", "task", "run"], sort=False):
        cues = run_ev[run_ev["trial_type"].isin(CLASSES)].sort_values("onset")
        if cues.empty:
            continue
        if task not in INTERFACES:
            raise ValueError(f"Cued run with unknown task {task!r}")
        feedback = run_ev.loc[run_ev["trial_type"] == "start_feedback", "onset"]
        trial_end = run_ev.loc[run_ev["trial_type"] == "end_trial", "onset"]
        cue_onsets = cues["onset"].to_numpy()
        for i, (onset, label) in enumerate(zip(cue_onsets, cues["trial_type"])):
            limit = cue_onsets[i + 1] if i + 1 < len(cue_onsets) else float("inf")
            rows.append(dict(
                subject=subject, session=session, task=task, run=run,
                interface=INTERFACES[task],
                mode="online" if task.startswith("Online") else "acquisition",
                onset=onset, label=label,
                feedback_delay=_next_onset_after(feedback, onset, limit) - onset,
                trial_end=_next_onset_after(trial_end, onset, limit) - onset,
            ))
    trials = pd.DataFrame(rows)
    return trials.sort_values(["subject", "session", "run", "onset"],
                              ignore_index=True)
