import math

import pandas as pd
import pytest

from src.bids_metadata import cue_trials, load_events, parse_entities


def test_parse_entities():
    ent = parse_entities("sub-P01_ses-2_task-OnlineRawGraz_run-3_events.tsv")
    assert ent == {"sub": "P01", "ses": "2", "task": "OnlineRawGraz", "run": 3}


def test_parse_entities_without_run():
    assert parse_entities("sub-P01_sessions.tsv") == {"sub": "P01"}


def _events(rows):
    return pd.DataFrame(rows, columns=["onset", "trial_type"])


def _write_run(root, sub, ses, task, run, rows):
    d = root / f"sub-{sub}" / f"ses-{ses}" / "eeg"
    d.mkdir(parents=True, exist_ok=True)
    name = f"sub-{sub}_ses-{ses}_task-{task}_run-{run}_events.tsv"
    _events(rows).to_csv(d / name, sep="\t", index=False)


@pytest.fixture
def bids_root(tmp_path):
    # Two cued trials in a Graz online run, one in a BrainHero calibration
    # run, and a baseline run without cues.
    _write_run(tmp_path, "P01", 1, "OnlineRawGraz", 3, [
        (6.5, "word"), (9.5, "start_feedback"), (14.5, "end_trial"),
        (19.0, "sub"), (22.0, "start_feedback"), (27.0, "end_trial"),
    ])
    _write_run(tmp_path, "P01", 1, "AcquisitionBH", 2, [
        (10.0, "mi"), (13.0, "start_feedback"), (18.0, "end_trial"),
    ])
    _write_run(tmp_path, "P01", 1, "BaselineOE", 0, [(0.0, "start_experiment")])
    return tmp_path


def test_load_events_adds_entities(bids_root):
    ev = load_events(bids_root)
    assert len(ev) == 10
    assert set(ev["task"]) == {"OnlineRawGraz", "AcquisitionBH", "BaselineOE"}
    assert ev.loc[ev["task"] == "OnlineRawGraz", "run"].unique().tolist() == [3]


def test_load_events_empty_dir_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_events(tmp_path)


def test_cue_trials_labels_order_and_timing(bids_root):
    trials = cue_trials(load_events(bids_root))
    # Baseline run has no cue -> no trial; rows in acquisition (run) order.
    assert trials["label"].tolist() == ["mi", "word", "sub"]
    assert trials["run"].tolist() == [2, 3, 3]
    assert trials["interface"].tolist() == ["BrainHero", "Graz", "Graz"]
    assert trials["mode"].tolist() == ["acquisition", "online", "online"]
    assert trials["feedback_delay"].tolist() == [3.0, 3.0, 3.0]
    assert trials["trial_end"].tolist() == [8.0, 8.0, 8.0]


def test_cue_trials_does_not_borrow_next_trials_events():
    # Trial 1 is missing its feedback marker: it must be NaN, not the
    # feedback of trial 2.
    ev = _events([(0.0, "mi"), (8.0, "end_trial"),
                  (10.0, "sub"), (13.0, "start_feedback")])
    ev.insert(0, "subject", "P01")
    ev.insert(1, "session", "1")
    ev.insert(2, "task", "OnlineRawGraz")
    ev.insert(3, "run", 3)
    trials = cue_trials(ev)
    assert math.isnan(trials.loc[0, "feedback_delay"])
    assert trials.loc[1, "feedback_delay"] == 3.0


def test_cue_trials_unknown_task_raises():
    ev = _events([(0.0, "mi")])
    for col, val in [("subject", "P01"), ("session", "1"),
                     ("task", "Mystery"), ("run", 1)]:
        ev[col] = val
    with pytest.raises(ValueError, match="unknown task"):
        cue_trials(ev)
