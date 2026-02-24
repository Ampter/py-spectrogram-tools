import sys
import os
from pathlib import Path

# Add scripts directory to sys.path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.append(str(scripts_dir))

# Import bump_version.py
from bump_version import bump_version

def test_bump_logic():
    test_cases = [
        ("1.0.0", "1.0.1"),
        ("1.0.8", "1.0.9"),
        ("1.0.9", "1.1.0"),
        ("1.1.0", "1.1.1"),
        ("1.1.9", "2.0.0"),
        ("2.1.9", "3.0.0"),
    ]

    for current, expected in test_cases:
        actual = bump_version(current)
        assert actual == expected, f"Failed: {current} -> {actual} (expected {expected})"
if __name__ == "__main__":
    test_bump_logic()
    print("Versioning tests passed!")
