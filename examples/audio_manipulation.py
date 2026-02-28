import pyspectools2 as pst
import numpy as np
import os
import tempfile


def main():
    # 1. Create some synthetic audio data
    print("Generating synthetic audio data...")
    duration = 2.0  # seconds
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    # A simple A4 tone (440 Hz)
    audio_mono = 0.5 * np.sin(2 * np.pi * 440 * t)

    # 2. Demonstrate to_stereo and to_mono
    print("\nDemonstrating channel conversion:")
    audio_stereo = pst.to_stereo(audio_mono)
    print(f"Mono shape: {audio_mono.shape}")
    print(f"Stereo shape: {audio_stereo.shape}")

    back_to_mono = pst.to_mono(audio_stereo)
    print(f"Back to mono shape: {back_to_mono.shape}")

    # 3. Demonstrate normalization and trimming
    print("\nDemonstrating normalization and trimming:")
    # Add some silence and low volume
    quiet_audio = np.concatenate(
        [np.zeros(10000), audio_mono * 0.1, np.zeros(10000)])
    print(f"Original max amplitude: {np.max(np.abs(quiet_audio)):.4f}")
    print(f"Original length: {len(quiet_audio)} samples")

    normalized = pst.normalize_audio(quiet_audio)
    print(f"Normalized max amplitude: {np.max(np.abs(normalized)):.4f}")

    trimmed = pst.trim_silence(normalized)
    print(f"Trimmed length: {len(trimmed)} samples")

    # 4. Demonstrate WAV info
    print("\nDemonstrating WAV info:")
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_wav = os.path.join(temp_dir, "test.wav")
        pst.save_wav(temp_wav, audio_mono, sample_rate)

        info = pst.get_wav_info(temp_wav)
        print(f"WAV Info for {os.path.basename(temp_wav)}:")
        for key, value in info.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
