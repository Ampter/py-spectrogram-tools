import sys
import tempfile
import types
import unittest
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


class TestDefaultDirectory(unittest.TestCase):
    @mock.patch("pyspectools2.spectrogram.Path.home", return_value=Path("/tmp/userhome"))
    @mock.patch("pyspectools2.spectrogram.platform.system", return_value="Linux")
    def test_default_directory_linux(self, *_):
        directory = spectrogram.get_default_directory()
        self.assertEqual(directory, "/tmp/userhome/SOUNDS/spectrograms")

    @mock.patch("pyspectools2.spectrogram.Path.home", return_value=Path("C:/Users/tester"))
    @mock.patch("pyspectools2.spectrogram.platform.system", return_value="Windows")
    def test_default_directory_windows(self, *_):
        directory = spectrogram.get_default_directory()
        self.assertEqual(directory, "C:/Users/tester/SOUNDS/spectrograms")

    @mock.patch("pyspectools2.spectrogram.Path.home", return_value=Path("/Users/tester"))
    @mock.patch("pyspectools2.spectrogram.platform.system", return_value="Darwin")
    def test_default_directory_macos(self, *_):
        directory = spectrogram.get_default_directory()
        self.assertEqual(directory, "/Users/tester/SOUNDS/spectrograms")


class TestSessionManagement(unittest.TestCase):
    def test_create_session_ignores_unrelated_and_malformed_entries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            Path(temp_dir, "session_1").mkdir()
            Path(temp_dir, "session_bad").mkdir()
            Path(temp_dir, "notes.txt").write_text(
                "not a session", encoding="utf-8")

            created = spectrogram.create_session_folder(temp_dir)

            self.assertTrue(created.endswith("session_2"))

    def test_create_session_uses_next_max_even_if_gaps_exist(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            Path(temp_dir, "session_1").mkdir()
            Path(temp_dir, "session_4").mkdir()

            created = spectrogram.create_session_folder(temp_dir)

            self.assertTrue(created.endswith("session_5"))

    def test_get_latest_session_folder_ignores_malformed_entries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            Path(temp_dir, "session_2").mkdir()
            Path(temp_dir, "session_10").mkdir()
            Path(temp_dir, "session_notanumber").mkdir()

            latest = spectrogram.get_latest_session_folder(temp_dir)

            self.assertTrue(latest.endswith("session_10"))


if __name__ == "__main__":
    unittest.main()
