from pyspectools2 import spectrogram
import pyspectools2
import sys
import types
import os
import tempfile
from unittest import mock
import numpy as np
import soundfile as sf
import pytest

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

fake_sounddevice = types.ModuleType("sounddevice")
fake_sounddevice.rec = lambda *args, **kwargs: []
fake_sounddevice.wait = lambda: None
sys.modules.setdefault("sounddevice", fake_sounddevice)


def test_save_and_load_wav():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = os.path.join(temp_dir, "test.wav")
        data = np.array([0.1, -0.2, 0.3, -0.4], dtype=np.float32)
        sr = 16000
        pyspectools2.save_wav(path, data, sr)
        assert os.path.exists(path)
        loaded_data, loaded_sr = pyspectools2.load_wav(path)
        assert loaded_sr == sr
        assert np.allclose(data, loaded_data, atol=1e-4)


def test_get_wav_info():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = os.path.join(temp_dir, "test.wav")
        data = np.array([0.1, -0.2], dtype=np.float32)
        sr = 16000
        pyspectools2.save_wav(path, data, sr)
        info = pyspectools2.get_wav_info(path)
        assert info["samplerate"] == 16000


def test_load_wavs_from_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        sr = 16000
        data = np.zeros(10, dtype=np.float32)
        sf.write(os.path.join(temp_dir, "one.wav"), data, sr)
        wavs = pyspectools2.load_wavs_from_directory(temp_dir)
        assert len(wavs) == 1


@mock.patch("pyspectools2.spectrogram.create_session_folder")
@mock.patch("pyspectools2.spectrogram.plot_spectrogram")
def test_batch_process_wavs(mock_plot, mock_create):
    """
    Test the batch processing loop.
    Note: save_spectrogram is not mocked here because batch_process_wavs
    now uses fig.savefig() directly in your updated spectrogram.py.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        sr = 16000
        # 512 samples to avoid NFFT warnings
        data = np.zeros(512, dtype=np.float32)
        sf.write(os.path.join(temp_dir, "test.wav"), data, sr)

        # Setup Mock behavior
        mock_create.return_value = temp_dir  # Save PNGs in the temp dir

        # Mock the Figure object and its savefig method
        mock_fig = mock.Mock()
        mock_ax = mock.Mock()
        mock_plot.return_value = (mock_fig, mock_ax)

        # Execute
        pyspectools2.batch_process_wavs(temp_dir)

        # Assertions
        mock_create.assert_called_once()
        mock_plot.assert_called_once()
        mock_fig.savefig.assert_called_once()
        mock_fig.clear.assert_called_once()
