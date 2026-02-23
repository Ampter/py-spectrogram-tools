"""Public package API for py-spectrogram-tools."""

__version__ = "1.0.0"

from .spectrogram import (
    create_session_folder,
    delete_latest_session_folder,
    get_default_directory,
    get_folder_size,
    get_latest_session_folder,
    plot_spectrogram,
    print_folder_size,
    record_audio,
    save_spectrogram,
)

__all__ = [
    "create_session_folder",
    "delete_latest_session_folder",
    "get_default_directory",
    "get_folder_size",
    "get_latest_session_folder",
    "plot_spectrogram",
    "print_folder_size",
    "record_audio",
    "save_spectrogram",
]
