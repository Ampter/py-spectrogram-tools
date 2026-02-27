import os
import platform
import re
import shutil
import time
from pathlib import Path
import matplotlib.pyplot as plt
import sounddevice as sd
import numpy as np
import soundfile as sf
from typing import Tuple, List, Dict, Optional

_SESSION_PATTERN = re.compile(r"^session_(\d+)$")


def load_wav(path: str) -> Tuple[np.ndarray, int]:
    """
    Load WAV file and return mono float32 numpy array + samplerate.
    """

    with sf.SoundFile(path) as f:
        data: np.ndarray = f.read(dtype="float32", always_2d=True)
        sr: int = f.samplerate

    # Convert stereo → mono if needed
    if data.ndim == 2 and data.shape[1] > 1:
        data = data.mean(axis=1)
    elif data.ndim == 2 and data.shape[1] == 1:
        data = data.flatten()

    return data, sr


def load_wavs_from_directory(directory: str) -> Dict[str, Tuple[np.ndarray, int]]:
    """
    Load all WAV files from a directory.

    Returns:
        dict mapping filename -> (audio_data, samplerate)
    """
    wavs: Dict[str, Tuple[np.ndarray, int]] = {}

    for file in os.listdir(directory):
        if file.lower().endswith(".wav"):
            path = os.path.join(directory, file)
            wavs[file] = load_wav(path)

    return wavs


def load_and_plot_wav(path, session=True):
    """
    Load a wav file, plot its spectrogram, and optionally save it to a session.
    """
    from . import plot_spectrogram, create_session_folder, save_spectrogram

    data, sr = load_wav(path)  # get samples and sample rate

    fig, ax = plot_spectrogram(data, rate=sr)

    if session:
        folder = create_session_folder()
        outfile = save_spectrogram(fig, folder)
        print(f"Saved spectrogram to: {outfile}")
        return fig, ax, outfile
    else:
        return fig, ax


def get_default_directory() -> str:
    """Return the default directory based on the operating system."""
    system = platform.system().lower()
    home_dir = Path.home()

    if system in {"windows", "darwin", "linux"}:
        return str(home_dir / "SOUNDS" / "spectrograms")

    raise OSError("Unsupported operating system")


def _get_session_numbers(directory: str) -> list[int]:
    """Collect valid session numbers from directory entries."""
    session_numbers: list[int] = []
    for entry in os.listdir(directory):
        full_path = os.path.join(directory, entry)
        if not os.path.isdir(full_path):
            continue

        match = _SESSION_PATTERN.match(entry)
        if match:
            session_numbers.append(int(match.group(1)))

    return session_numbers


def create_session_folder(directory=None) -> str:
    """Create a new session folder inside the provided directory."""
    if directory is None:
        directory = get_default_directory()

    os.makedirs(directory, exist_ok=True)

    next_number = max(_get_session_numbers(directory), default=0) + 1
    while True:
        session_folder = os.path.join(directory, f"session_{next_number}")
        try:
            os.makedirs(session_folder, exist_ok=False)
            print(f"Created new session: {session_folder}")
            return session_folder
        except FileExistsError:
            next_number += 1


def get_latest_session_folder(directory=None) -> str | None:
    """Find the session folder with the highest number and return its path."""
    if directory is None:
        directory = get_default_directory()

    if not os.path.exists(directory):
        return None

    session_numbers = _get_session_numbers(directory)
    if not session_numbers:
        return None

    latest_session = max(session_numbers)
    return os.path.join(directory, f"session_{latest_session}")


def plot_spectrogram(audio_data, rate=44100) -> tuple:
    """Plot the spectrogram of the given audio data."""
    fig, ax = plt.subplots()
    ax.set_title("Spectrogram")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (Hz)")
    ax.specgram(audio_data, NFFT=256, Fs=rate, noverlap=128)
    return fig, ax


def save_spectrogram(fig, session_folder) -> str:
    """Save the generated spectrogram plot to the session folder."""
    timestamp = time.ctime().replace(" ", "_").replace(":", "-")
    filename = os.path.join(session_folder, f"spectrogram_{timestamp}.png")
    fig.savefig(filename)
    plt.close(fig)
    return filename


def record_audio(duration=3, rate=44100, channels=1):
    """Record audio data and return it as a flattened array."""
    print("Starting recording...")
    audio_data = sd.rec(int(rate * duration),
                        samplerate=rate, channels=channels)
    sd.wait()
    print("Recording finished.")
    return audio_data.flatten()


def delete_latest_session_folder(directory=None):
    """Delete the latest session folder."""
    if directory is None:
        directory = get_default_directory()

    latest_session_folder = get_latest_session_folder(directory)
    if latest_session_folder is None:
        print("No session folders found to delete.")
        return

    try:
        shutil.rmtree(latest_session_folder)
        print(f"Deleted the latest session folder: {latest_session_folder}")
    except Exception as exc:
        print(f"Error deleting the folder: {exc}")


def get_folder_size(directory=None):
    """Calculate the total size of a directory."""
    if directory is None:
        directory = get_default_directory()

    total_size = 0
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    return total_size


def print_folder_size(directory=None):
    """Print the total size of the latest session folder."""
    if directory is None:
        directory = get_default_directory()

    latest_session_folder = get_latest_session_folder(directory)
    if latest_session_folder is None:
        print("No session folder found.")
        return

    total_size = get_folder_size(latest_session_folder)
    print(
        f"Total size of folder {latest_session_folder}: {total_size / (1024 * 1024):.2f} MB"
    )


def plot_all_wavs(directory: str, session: bool = True):
    """
    Load and plot all WAV files in a directory.
    """
    results = []

    for file in os.listdir(directory):
        if file.lower().endswith(".wav"):
            path = os.path.join(directory, file)
            result = load_and_plot_wav(path, session=session)
            results.append((file, result))

    return results


def record_and_save_wav(duration=3, rate=44100, channels=1, directory=None) -> str:
    """
    Record audio and save as WAV file inside a new session folder.
    """
    if directory is None:
        directory = get_default_directory()

    session_folder = create_session_folder(directory)

    audio_data = record_audio(duration=duration, rate=rate, channels=channels)

    timestamp = time.ctime().replace(" ", "_").replace(":", "-")
    filename = os.path.join(session_folder, f"recording_{timestamp}.wav")

    sf.write(filename, audio_data, rate)

    print(f"Saved recording to: {filename}")
    return filename


def play_wav(path: str):
    """
    Play a WAV file.
    """
    data, sr = load_wav(path)
    sd.play(data, sr)
    sd.wait()


def save_wav(path: str, audio_data: np.ndarray, samplerate: int):
    """
    Save numpy audio array to WAV file.
    """
    sf.write(path, audio_data, samplerate)


def normalize_audio(audio_data: np.ndarray) -> np.ndarray:
    """
    Normalize audio to range [-1, 1].
    """
    max_val = np.max(np.abs(audio_data))
    if max_val == 0:
        return audio_data
    return audio_data / max_val


def trim_silence(audio_data: np.ndarray, threshold=0.01) -> np.ndarray:
    """
    Remove leading and trailing silence.
    """
    mask = np.abs(audio_data) > threshold
    if not np.any(mask):
        return audio_data

    start = np.argmax(mask)
    end = len(audio_data) - np.argmax(mask[::-1])
    return audio_data[start:end]


def batch_process_wavs(directory: str):
    """
    Load, normalize, trim, plot, and save all WAV files in directory.
    """
    session_folder = create_session_folder()

    for file in os.listdir(directory):
        if not file.lower().endswith(".wav"):
            continue

        path = os.path.join(directory, file)
        data, sr = load_wav(path)

        data = normalize_audio(data)
        data = trim_silence(data)

        fig, ax = plot_spectrogram(data, rate=sr)
        outfile = save_spectrogram(fig, session_folder)

        print(f"Processed {file} -> {outfile}")


def get_wav_info(path: str) -> dict:
    """
    Return metadata about WAV file.
    """
    with sf.SoundFile(path) as f:
        return {
            "samplerate": f.samplerate,
            "channels": f.channels,
            "frames": f.frames,
            "duration_sec": f.frames / f.samplerate,
            "format": f.format,
            "subtype": f.subtype,
        }


def to_mono(audio_data: np.ndarray) -> np.ndarray:
    if audio_data.ndim == 2:
        return audio_data.mean(axis=1)
    return audio_data


def to_stereo(audio_data: np.ndarray) -> np.ndarray:
    if audio_data.ndim == 1:
        return np.column_stack([audio_data, audio_data])
    return audio_data
