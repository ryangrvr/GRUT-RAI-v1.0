import csv
from pathlib import Path

import pytest

from tools.audit_all import _assert_monotonic, _read_csv_rows, _validate_cosmology_outputs


def test_read_csv_rows_skips_comments(tmp_path: Path):
    path = tmp_path / "test.csv"
    path.write_text("# header note\na,b\n1,2\n")
    rows = _read_csv_rows(path)
    assert rows == [{"a": "1", "b": "2"}]


def test_assert_monotonic():
    _assert_monotonic([1.0, 1.0, 2.0])
    with pytest.raises(ValueError):
        _assert_monotonic([2.0, 1.0])


def test_validate_cosmology_outputs_ok():
    outputs = {
        "OBS_HZ_001": {"z": [2.0, 1.0], "H": [1.0, 2.0]},
        "OBS_FS8_001": {"fsigma8": [0.1, 0.2], "fs8_mask": [False, False]},
    }
    _validate_cosmology_outputs(outputs, steps=2)


def test_validate_cosmology_outputs_bad_length():
    outputs = {"OBS_HZ_001": {"z": [2.0], "H": [1.0]}}
    with pytest.raises(ValueError):
        _validate_cosmology_outputs(outputs, steps=2)