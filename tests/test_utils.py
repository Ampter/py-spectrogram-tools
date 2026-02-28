import pyspectools2 as pst
import os
import sys
import types
import tempfile
from pathlib import Path
from unittest import mock
import numpy as np
import pytest

# --- Setup Mocks for Hardware/Visuals BEFORE Project Imports ---
# This prevents tests from trying to open windows or access mic hardware
fake_matplotlib = types.ModuleType("matplotlib")
fake_pyplot = types.ModuleType("pyplot")
fake_figure = types.ModuleType("figure")
fake_agg = types.ModuleType("backend_agg")

fake_figure.Figure = mock.Mock()
fake_agg.FigureCanvasAgg = mock.Mock()
fake_pyplot.subplots = lambda: (mock.Mock(), mock.Mock())
fake_pyplot.close = lambda fig: None
fake_matplotlib.pyplot = fake_pyplot

sys.modules.setdefault("matplotlib", fake_matplotlib)
sys.modules.setdefault("matplotlib.pyplot", fake_pyplot)
sys.modules.setdefault("matplotlib.figure", fake_figure)
sys.modules.setdefault("matplotlib.backends.backend_agg", fake_agg)

fake_sd = types.ModuleType("sounddevice")
fake_sd.rec = mock.Mock()
fake_sd.wait = mock.Mock()
fake_sd.play = mock.Mock()
sys.modules.setdefault("sounddevice", fake_sd)


def test_channel_conversions():
    """Verify mono <-> stereo transformations."""
    # Mono to Stereo
    mono = np.array([0.1, -0.2, 0.5])
    stereo = pst.to_stereo(mono)
    assert stereo.shape == (3, 2)
    assert np.array_equal(stereo[:, 0], mono)
    assert np.array_equal(stereo[:, 1], mono)

    # Stereo to Mono (averaging)
    test_stereo = np.array([[0.1, 0.3], [-0.2, -0.4]])
    mono_out = pst.to_mono(test_stereo)
    assert mono_out.shape == (2,)
    # (0.1 + 0.3) / 2 = 0.2
    assert mono_out[0] == pytest.approx(0.2)
    assert mono_out[1] == pytest.approx(-0.3)


def test_session_directory_logic():
    """Verify session folder creation, retrieval, and deletion."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # 1. Create sessions
        s1 = pst.create_session_folder(tmp_dir)
        s2 = pst.create_session_folder(tmp_dir)
        assert os.path.basename(s1) == "session_1"
        assert os.path.basename(s2) == "session_2"

        # 2. Get latest
        latest = pst.get_latest_session_folder(tmp_dir)
        assert latest == s2

        # 3. Delete latest
        pst.delete_latest_session_folder(tmp_dir)
        assert not os.path.exists(s2)
        assert os.path.exists(s1)


def test_folder_size_calculations():
    """Verify recursive folder size counting."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a 10 byte file in root
        with open(os.path.join(tmp_dir, "root.bin"), "wb") as f:
            f.write(b"0123456789")

        # Create a 5 byte file in subfolder
        sub = os.path.join(tmp_dir, "sub")
        os.mkdir(sub)
        with open(os.path.join(sub, "sub.bin"), "wb") as f:
            f.write(b"abcde")

        assert pst.get_folder_size(tmp_dir) == 15


@mock.patch("pyspectools2.spectrogram.sd.rec")
def test_record_audio_logic(mock_rec):
    """Verify record_audio calls sounddevice correctly."""
    sr = 44100
    duration = 1
    # Mock return value: 1 second of audio
    mock_rec.return_value = np.zeros((sr * duration, 1))

    # In your spectrogram.py, the argument is 'rate', not 'samplerate'
    audio = pst.record_audio(duration=duration, rate=sr)

    assert mock_rec.called
    assert len(audio) == sr * duration


def test_load_and_plot_wav_wrapper():
    """Verify the high-level wrapper coordinates load and plot calls."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Patch Path.home() so get_default_directory() correctly routes all internal IO to tmp_dir
        with mock.patch("pyspectools2.spectrogram.Path.home", return_value=Path(tmp_dir)):
            with mock.patch("pyspectools2.spectrogram.load_wav") as mock_load:

                # Use random noise (instead of zeros) to avoid matplotlib log10(0) divide by zero warnings
                mock_load.return_value = (np.random.rand(2048), 16000)

                pst.load_and_plot_wav("dummy.wav")

                mock_load.assert_called_with("dummy.wav")

                # Verify that a plot was actually saved somewhere in the tmp_dir tree
                png_found = False
                for root, dirs, files in os.walk(tmp_dir):
                    if any(f.endswith(".png") for f in files):
                        png_found = True
                        break

                assert png_found, f"Expected a .png file to be saved in the temporary directory tree {tmp_dir}."


@mock.patch("pyspectools2.spectrogram.sd.play")
@mock.patch("pyspectools2.spectrogram.load_wav")
def test_play_wav_logic(mock_load, mock_play):
    """Verify play_wav calls sounddevice play."""
    # Mock the loading of the file with a larger random array
    mock_load.return_value = (np.random.rand(2048), 16000)

    pst.play_wav("some_file.wav")

    mock_load.assert_called_with("some_file.wav")
    assert mock_play.called
