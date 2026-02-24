import sys
import tempfile
import types
from pathlib import Path
from unittest import mock

# Lightweight stubs so tests can run without optional runtime dependencies.
fake_matplotlib = types.ModuleType("matplotlib")
fake_pyplot = types.ModuleType("pyplot")
fake_pyplot.subplots = lambda: (object(), object())
fake_pyplot.close = lambda fig: None
fake_matplotlib.pyplot = fake_pyplot
sys.modules.setdefault("matplotlib", fake_matplotlib)
sys.modules.setdefault("matplotlib.pyplot", fake_pyplot)

fake_sounddevice = types.ModuleType("sounddevice")
fake_sounddevice.rec = lambda *args, **kwargs: []
fake_sounddevice.wait = lambda: None
sys.modules.setdefault("sounddevice", fake_sounddevice)

from pyspectools2 import spectrogram  # noqa: E402


def test_default_directory_linux():
    with mock.patch("pyspectools2.spectrogram.Path.home", return_value=Path("/tmp/userhome")), \
         mock.patch("pyspectools2.spectrogram.platform.system", return_value="Linux"):
        directory = spectrogram.get_default_directory()
    assert directory == "/tmp/userhome/SOUNDS/spectrograms"


def test_default_directory_windows():
    with mock.patch("pyspectools2.spectrogram.Path.home", return_value=Path("C:/Users/tester")), \
         mock.patch("pyspectools2.spectrogram.platform.system", return_value="Windows"):
        directory = spectrogram.get_default_directory()
    assert directory == "C:/Users/tester/SOUNDS/spectrograms"


def test_default_directory_macos():
    with mock.patch("pyspectools2.spectrogram.Path.home", return_value=Path("/Users/tester")), \
         mock.patch("pyspectools2.spectrogram.platform.system", return_value="Darwin"):
        directory = spectrogram.get_default_directory()
    assert directory == "/Users/tester/SOUNDS/spectrograms"


def test_default_directory_unsupported_os():
    with mock.patch("pyspectools2.spectrogram.platform.system", return_value="Plan9"):
        try:
            spectrogram.get_default_directory()
            assert False, "Expected OSError for unsupported OS"
        except OSError:
            pass


def test_get_session_numbers_ignores_invalid_entries():
    with tempfile.TemporaryDirectory() as temp_dir:
        Path(temp_dir, "session_1").mkdir()
        Path(temp_dir, "session_notnum").mkdir()
        Path(temp_dir, "session_02").mkdir()
        Path(temp_dir, "note.txt").write_text("x", encoding="utf-8")

        numbers = spectrogram._get_session_numbers(temp_dir)

    assert sorted(numbers) == [1, 2]


def test_create_session_ignores_unrelated_and_malformed_entries():
    with tempfile.TemporaryDirectory() as temp_dir:
        Path(temp_dir, "session_1").mkdir()
        Path(temp_dir, "session_bad").mkdir()
        Path(temp_dir, "notes.txt").write_text("not a session", encoding="utf-8")

        created = spectrogram.create_session_folder(temp_dir)

        assert created.endswith("session_2")


def test_create_session_uses_next_max_even_if_gaps_exist():
    with tempfile.TemporaryDirectory() as temp_dir:
        Path(temp_dir, "session_1").mkdir()
        Path(temp_dir, "session_4").mkdir()

        created = spectrogram.create_session_folder(temp_dir)

        assert created.endswith("session_5")


def test_get_latest_session_folder_ignores_malformed_entries():
    with tempfile.TemporaryDirectory() as temp_dir:
        Path(temp_dir, "session_2").mkdir()
        Path(temp_dir, "session_10").mkdir()
        Path(temp_dir, "session_notanumber").mkdir()

        latest = spectrogram.get_latest_session_folder(temp_dir)

        assert latest.endswith("session_10")


def test_save_spectrogram_uses_expected_filename_and_closes_figure():
    class DummyFig:
        def __init__(self):
            self.saved_to = None

        def savefig(self, path):
            self.saved_to = path

    fig = DummyFig()
    with tempfile.TemporaryDirectory() as temp_dir, \
         mock.patch("pyspectools2.spectrogram.time.ctime", return_value="Mon Jan  1 12:00:00 2026"), \
         mock.patch("pyspectools2.spectrogram.plt.close") as close_mock:
        out = spectrogram.save_spectrogram(fig, temp_dir)

    assert out.startswith(f"{temp_dir}/spectrogram_")
    assert out.endswith(".png")
    assert "Mon_Jan__1_12-00-00_2026" in out
    assert fig.saved_to == out
    close_mock.assert_called_once_with(fig)


def test_delete_latest_session_folder_when_none_exists(capsys):
    with tempfile.TemporaryDirectory() as temp_dir:
        spectrogram.delete_latest_session_folder(temp_dir)
        captured = capsys.readouterr()

    assert "No session folders found to delete." in captured.out


def test_delete_latest_session_folder_deletes_highest_numbered_folder():
    with tempfile.TemporaryDirectory() as temp_dir:
        Path(temp_dir, "session_1").mkdir()
        Path(temp_dir, "session_2").mkdir()

        spectrogram.delete_latest_session_folder(temp_dir)

        assert Path(temp_dir, "session_1").exists()
        assert not Path(temp_dir, "session_2").exists()


def test_get_folder_size_sums_nested_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        nested = Path(temp_dir, "a", "b")
        nested.mkdir(parents=True)
        Path(temp_dir, "f1.bin").write_bytes(b"12345")
        Path(nested, "f2.bin").write_bytes(b"abcd")

        total = spectrogram.get_folder_size(temp_dir)

    assert total == 9


def test_print_folder_size_prints_megabytes(capsys):
    with mock.patch("pyspectools2.spectrogram.get_latest_session_folder", return_value="/tmp/session_4"), \
         mock.patch("pyspectools2.spectrogram.get_folder_size", return_value=1048576):
        spectrogram.print_folder_size("/tmp/base")
        captured = capsys.readouterr()

    assert "Total size of folder /tmp/session_4: 1.00 MB" in captured.out


def test_print_folder_size_when_no_session(capsys):
    with mock.patch("pyspectools2.spectrogram.get_latest_session_folder", return_value=None):
        spectrogram.print_folder_size("/tmp/base")
        captured = capsys.readouterr()

    assert "No session folder found." in captured.out
