import sys
import types
from unittest import mock

# Mock sounddevice and matplotlib before importing pyspectools2
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

import numpy as np
import pytest
from pyspectools2 import normalize_audio, trim_silence, to_mono, to_stereo

def test_normalize_audio():
    audio = np.array([0.0, 0.5, -1.0, 2.0])
    normalized = normalize_audio(audio)
    assert np.max(np.abs(normalized)) == 1.0
    assert np.allclose(normalized, [0.0, 0.25, -0.5, 1.0])

def test_normalize_audio_zero():
    audio = np.zeros(10)
    normalized = normalize_audio(audio)
    assert np.array_equal(normalized, audio)

def test_trim_silence():
    audio = np.array([0.0, 0.0, 0.5, 0.8, 0.0, 0.1, 0.0, 0.0])
    trimmed = trim_silence(audio, threshold=0.2)
    # Starts at 0.5, ends after 0.8
    assert np.array_equal(trimmed, [0.5, 0.8])

def test_trim_silence_no_signal():
    audio = np.array([0.0, 0.005, 0.001])
    trimmed = trim_silence(audio, threshold=0.01)
    assert np.array_equal(trimmed, audio)

def test_to_mono():
    # Mono stays mono
    mono = np.array([0.1, 0.2, 0.3])
    assert np.array_equal(to_mono(mono), mono)

    # Stereo to mono
    stereo = np.array([[0.1, 0.3], [0.2, 0.4]])
    expected = np.array([0.2, 0.3])
    assert np.allclose(to_mono(stereo), expected)

def test_to_stereo():
    # Mono to stereo
    mono = np.array([0.1, 0.2])
    expected = np.array([[0.1, 0.1], [0.2, 0.2]])
    assert np.array_equal(to_stereo(mono), expected)

    # Stereo stays stereo
    stereo = np.array([[0.1, 0.3], [0.2, 0.4]])
    assert np.array_equal(to_stereo(stereo), stereo)
