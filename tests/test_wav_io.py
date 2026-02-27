import sys
import types
import os
import tempfile
from unittest import mock
import numpy as np
import soundfile as sf
import pytest

# Mock sounddevice and matplotlib before importing pyspectools2
fake_matplotlib = types.ModuleType("matplotlib")
fake_pyplot = types.ModuleType("pyplot")
fake_pyplot.subplots = lambda: (mock.Mock(), mock.Mock())
fake_pyplot.close = lambda fig: None
fake_matplotlib.pyplot = fake_pyplot
sys.modules.setdefault("matplotlib", fake_matplotlib)
sys.modules.setdefault("matplotlib.pyplot", fake_pyplot)

fake_sounddevice = types.ModuleType("sounddevice")
fake_sounddevice.rec = lambda *args, **kwargs: []
fake_sounddevice.wait = lambda: None
sys.modules.setdefault("sounddevice", fake_sounddevice)

from pyspectools2 import (
    load_wav, save_wav, get_wav_info,
    load_wavs_from_directory, batch_process_wavs
)

def test_save_and_load_wav():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = os.path.join(temp_dir, "test.wav")
        data = np.array([0.1, -0.2, 0.3, -0.4], dtype=np.float32)
        sr = 16000

        save_wav(path, data, sr)
        assert os.path.exists(path)

        loaded_data, loaded_sr = load_wav(path)
        assert loaded_sr == sr
        assert np.allclose(data, loaded_data, atol=1e-4)

def test_get_wav_info():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = os.path.join(temp_dir, "test.wav")
        data = np.array([0.1, -0.2], dtype=np.float32)
        sr = 16000
        save_wav(path, data, sr)

        info = get_wav_info(path)
        assert info["samplerate"] == 16000
        assert info["frames"] == 2
        assert info["duration_sec"] == 2 / 16000
        assert info["channels"] == 1

def test_load_wavs_from_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        sr = 16000
        data1 = np.zeros(10, dtype=np.float32)
        data2 = np.ones(10, dtype=np.float32)

        sf.write(os.path.join(temp_dir, "one.wav"), data1, sr)
        sf.write(os.path.join(temp_dir, "two.wav"), data2, sr)

        wavs = load_wavs_from_directory(temp_dir)
        assert len(wavs) == 2
        assert "one.wav" in wavs
        assert "two.wav" in wavs

@mock.patch("pyspectools2.spectrogram.create_session_folder")
@mock.patch("pyspectools2.spectrogram.save_spectrogram")
@mock.patch("pyspectools2.spectrogram.plot_spectrogram")
def test_batch_process_wavs(mock_plot, mock_save, mock_create):
    with tempfile.TemporaryDirectory() as temp_dir:
        sr = 16000
        data = np.zeros(10, dtype=np.float32)
        sf.write(os.path.join(temp_dir, "test.wav"), data, sr)

        mock_create.return_value = "/tmp/fake_session"
        mock_plot.return_value = (mock.Mock(), mock.Mock())
        mock_save.return_value = "/tmp/fake_session/test.png"

        batch_process_wavs(temp_dir)

        mock_create.assert_called_once()
        mock_plot.assert_called()
        mock_save.assert_called()
