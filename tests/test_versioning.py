from pyspectools2.scripts.bump_version import bump_version
import sys
from pathlib import Path
import pytest

@pytest.mark.parametrize(
    "current, expected",
    [
        ("1.0.0", "1.0.1"),
        ("1.0.8", "1.0.9"),
        ("1.0.9", "1.1.0"),
        ("1.1.0", "1.1.1"),
        ("1.1.9", "2.0.0"),
        ("2.1.9", "3.0.0"),
    ],
)
def test_bump_version_rules(current, expected):
    assert bump_version(current) == expected
