from pathlib import Path

import pytest

from src.splits import (OFFICIAL_SPLIT, assert_no_test_subjects,
                        official_split_from_kit, subject_label, subjects_in)

ROOT = Path(__file__).resolve().parents[1]
KIT_DATA = ROOT / "data" / "benchopt" / "neural_compet"
BIDS_META = ROOT / "data" / "nm000290_meta"


def test_split_sizes_are_60_20_20_of_ten_subjects():
    assert len(OFFICIAL_SPLIT) == 10
    assert [len(subjects_in(s)) for s in ("train", "val", "test")] == [6, 2, 2]


def test_subject_label_normalizes_kit_and_bids_names():
    assert subject_label("Dreyer2026Proteus/P04") == "P04"
    assert subject_label("sub-P04") == "P04"
    assert subject_label("P04") == "P04"


def test_guard_accepts_train_and_val_subjects():
    assert_no_test_subjects(subjects_in("train") + subjects_in("val"))


@pytest.mark.parametrize("subject", ["P04", "sub-P09", "Dreyer2026Proteus/P04"])
def test_guard_rejects_test_subjects_in_any_naming(subject):
    with pytest.raises(ValueError, match="test subjects"):
        assert_no_test_subjects(["P01", subject])


def test_guard_rejects_unknown_subjects():
    with pytest.raises(ValueError, match="not in the official split"):
        assert_no_test_subjects(["P11"])


def test_subjects_in_rejects_unknown_split():
    with pytest.raises(ValueError):
        subjects_in("validation")


@pytest.mark.integration
@pytest.mark.skipif(not KIT_DATA.exists(), reason="run scripts/prepare_data.sh")
def test_official_split_matches_kit():
    # The recorded split must equal what the pinned kit produces, and the
    # kit's windows must be exactly the cued trials in the BIDS events.
    split_of, windows = official_split_from_kit(KIT_DATA)
    assert split_of == OFFICIAL_SPLIT
    if BIDS_META.exists():
        from src.bids_metadata import cue_trials, load_events
        trials = cue_trials(load_events(BIDS_META))
        assert windows == trials["subject"].value_counts().to_dict()
