import os
import tempfile
import numpy as np
import pytest
import pyspectools2 as pst

def test_normalize_audio():
    """
    Test that normalize_audio scales the peak amplitude to 1.0.
    """
    # Create low-amplitude data (peak is 0.5)
    audio_data = np.array([-0.5, 0.0, 0.2, 0.5], dtype=np.float32)

    normalized = pst.normalize_audio(audio_data)
    # Peak absolute value should now be exactly 1.0

    assert np.max(np.abs(normalized)) == pytest.approx(1.0)
    # Check that proportions are maintained

    assert normalized[0] == -1.0
    assert normalized[2] == 0.4

def test_normalize_audio_zero_input():
    """
    Test that normalize_audio handles an all-zero array without crashing.
    """
    zeros = np.zeros(100, dtype=np.float32)
    normalized = pst.normalize_audio(zeros)
    assert np.array_equal(normalized, zeros)

def test_trim_silence():
    """
    Test that trim_silence removes leading and trailing zeros.
    """
    # [50 zeros, 100 ones (signal), 50 zeros]
    leading_silence = np.zeros(50)
    signal = np.ones(100)
    trailing_silence = np.zeros(50)
    audio_data = np.concatenate([leading_silence, signal, trailing_silence])
    
    trimmed = pst.trim_silence(audio_data, threshold=0.1)
    
    # Should be exactly the signal length
    assert len(trimmed) == 100
    assert np.all(trimmed == 1.0)

def test_trim_silence_no_signal():
    """
    Test trim_silence with a purely silent array.
    """
    silence = np.zeros(100)
    trimmed = pst.trim_silence(silence, threshold=0.1)
    # Should return the original array if nothing exceeds threshold
    assert len(trimmed) == 100

def test_wav_roundtrip():
    """
    Test saving a file and loading it back (I/O integrity).
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = os.path.join(tmp_dir, "roundtrip.wav")
        original_sr = 22050
        # Generate 0.1 seconds of a 440Hz sine wave
        t = np.linspace(0, 0.1, int(original_sr * 0.1))
        original_data = np.sin(2 * np.pi * 440 * t).astype(np.float32)
        
        # Save
        pst.save_wav(file_path, original_data, original_sr)
        assert os.path.exists(file_path)
        
        # Load
        loaded_data, loaded_sr = pst.load_wav(file_path)
        
        # Verify metadata
        assert loaded_sr == original_sr
        # Verify data content (allow for small float epsilon from compression/format)
        assert np.allclose(original_data, loaded_data, atol=1e-4)

def test_get_wav_info_integrity():
    """
    Verify get_wav_info correctly reports file metadata.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = os.path.join(tmp_dir, "info_test.wav")
        sr = 16000
        data = np.zeros(16000, dtype=np.float32) # 1 second
        pst.save_wav(file_path, data, sr)
        
        info = pst.get_wav_info(file_path)
        assert info["samplerate"] == 16000
        assert info["duration_sec"] == 1.0
        assert info["frames"] == 16000
        assert info["channels"] == 1
