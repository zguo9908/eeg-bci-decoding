"""The official public subject split, and a guard against test-set leakage.

Fact (read from the official pipeline, not reimplemented): NeuralBench 0.4.0
``_motor_imagery_stream`` splits PROTEUS by subject with neuralset's
``SklearnSplit`` (60/20/20, ``random_state=33``). Its result depends on that
random state *and* on the order NeuralBench lists the subjects, so it is
recorded here as data and re-checked against the kit by
``tests/test_splits.py::test_official_split_matches_kit`` (needs the data).
Verified identical under benchopt seeds 0 and 42 (kit a66bc23).

The warm-up test labels are public, so nothing but this guard stops test
subjects from leaking into training or model selection.
"""

import sys
from collections import Counter
from pathlib import Path

OFFICIAL_SPLIT = {
    "P01": "train", "P02": "train", "P03": "train", "P06": "train",
    "P07": "train", "P10": "train",
    "P05": "val", "P08": "val",
    "P04": "test", "P09": "test",
}

KIT_TRACK = (Path(__file__).resolve().parents[1]
             / "external" / "2026-competition" / "tracks" / "bci_decoding")


def subject_label(subject):
    """``"Dreyer2026Proteus/P01"`` (kit) or ``"sub-P01"`` (BIDS) -> ``"P01"``."""
    label = str(subject).rsplit("/", 1)[-1]
    return label.removeprefix("sub-")


def subjects_in(split):
    """Sorted subject labels of ``split`` ("train", "val" or "test")."""
    if split not in {"train", "val", "test"}:
        raise ValueError(f"Unknown split {split!r}")
    return sorted(s for s, sp in OFFICIAL_SPLIT.items() if sp == split)


def assert_no_test_subjects(subjects):
    """Raise ``ValueError`` if any of ``subjects`` is an official test subject.

    Call this on every set of subjects used for fitting, normalization
    statistics, feature or hyperparameter selection, or model selection.
    Unknown subjects also raise: an unrecorded subject could be anyone.
    """
    labels = {subject_label(s) for s in subjects}
    unknown = sorted(labels - OFFICIAL_SPLIT.keys())
    if unknown:
        raise ValueError(f"Subjects not in the official split: {unknown}")
    leaked = sorted(s for s in labels if OFFICIAL_SPLIT[s] == "test")
    if leaked:
        raise ValueError(f"Official test subjects used for development: {leaked}")


def official_split_from_kit(data_dir, seed=42):
    """Read the split from the kit's own loaders (needs the prepared data).

    Returns ``(split_of_subject, windows_per_subject)``. Slow (builds the
    NeuralBench pipeline); used to verify ``OFFICIAL_SPLIT``, not in modelling.
    """
    sys.path.insert(0, str(KIT_TRACK))
    from benchmark_utils.nb_task import load_task

    loaders, _ = load_task("eeg", "_motor_imagery_stream",
                           data_dir=data_dir, seed=seed)
    split_of, windows = {}, Counter()
    for split, loader in loaders.items():
        for seg in loader.loader.dataset.seg_ds.segments:
            subject = subject_label(seg.trigger.to_dict()["subject"])
            if split_of.setdefault(subject, split) != split:
                raise AssertionError(f"{subject} is in two splits")
            windows[subject] += 1
    return split_of, dict(windows)
