import re
from pathlib import Path


def _read_version_from_init() -> str:
    init_text = Path("pyspectools2/__init__.py").read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init_text)
    assert match, "__version__ must be defined in pyspectools2/__init__.py"
    return match.group(1)


def test_pyproject_version_source_is_init_file():
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.hatch.version]" in pyproject
    assert 'path = "pyspectools2/__init__.py"' in pyproject


def test_setup_reads_version_from_init():
    setup_text = Path("setup.py").read_text(encoding="utf-8")
    assert "VERSION_MATCH = re.search" in setup_text
    assert "version=VERSION_MATCH.group(1)" in setup_text


def test_setup_and_init_resolve_same_version_value():
    setup_text = Path("setup.py").read_text(encoding="utf-8")
    init_version = _read_version_from_init()

    setup_init_match = re.search(
        r'INIT_TEXT\s*=\s*Path\("pyspectools2/__init__\.py"\)\.read_text',
        setup_text,
    )
    assert setup_init_match, "setup.py should read version from pyspectools2/__init__.py"
    assert isinstance(init_version, str) and init_version.count(".") == 2
