import os
import platform
import re
import shutil
import time
from pathlib import Path

import matplotlib.pyplot as plt
import sounddevice as sd

_SESSION_PATTERN = re.compile(r"^session_(\d+)$")


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
    audio_data = sd.rec(int(rate * duration), samplerate=rate, channels=channels)
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
