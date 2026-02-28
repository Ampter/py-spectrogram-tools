# Spectrogram Recorder Library

`pyspectools2` is a Python library for recording audio, generating spectrograms, and managing numbered recording sessions.

## Who this is for

This package is useful if you want a lightweight way to:
- record short audio clips from a microphone,
- visualize them as spectrograms,
- save outputs into incremental session folders.

## Features

- Record audio from your default input device (`sounddevice`).
- Plot and save spectrograms (`matplotlib`).
- Create numbered session folders (`session_1`, `session_2`, ...).
- Delete the latest session and inspect folder sizes.
- Use a cross-platform default save location based on your home directory.
- Load, save, and process WAV files.
- Audio utilities: normalization, trimming, mono/stereo conversion.

## Installation

```bash
pip install pyspectools2
```

Or from source:

```bash
git clone https://github.com/Ampter/pyspectools2
cd pyspectools2
pip install .
```

## Runtime requirements

- Python 3.10+
- A working audio input device and backend supported by `sounddevice`
- Optional display backend for interactive plotting (headless CI can still run tests with mocks)

## Quickstart

```python
import pyspectools2 as pst

session_folder = pst.create_session_folder()
audio_data = pst.record_audio(duration=5)
fig, _ = pst.plot_spectrogram(audio_data)
output_file = pst.save_spectrogram(fig, session_folder)

print(f"Saved spectrogram: {output_file}")
```

Expected behavior:
- A folder like `.../SOUNDS/spectrograms/session_1` is created.
- Console shows recording start/finish messages.
- A file named like `spectrogram_Mon_Jan_01_12-00-00_2026.png` is saved.

## API reference

### Session management

#### `pst.get_default_directory()`
Returns the default directory for spectrogram sessions:
- Windows: `C:\Users\<username>\SOUNDS\spectrograms`
- macOS: `/Users/<username>/SOUNDS/spectrograms`
- Linux: `/home/<username>/SOUNDS/spectrograms`

#### `pst.create_session_folder(directory=None)`
Creates a new folder such as `session_5` and returns its path.

#### `pst.get_latest_session_folder(directory=None)`
Returns the highest numbered session folder path, or `None` if absent.

#### `pst.delete_latest_session_folder(directory=None)`
Deletes the latest numbered session folder.

### Recording and plotting

#### `pst.record_audio(duration=3, rate=44100, channels=1)`
Records audio and returns a flattened NumPy array.

#### `pst.plot_spectrogram(audio_data, rate=44100)`
Returns `(fig, ax)` for the generated spectrogram.

#### `pst.save_spectrogram(fig, session_folder)`
Saves a PNG in the target session folder and returns the output file path.

### WAV and Audio processing

#### `pst.load_wav(path)`
Loads a WAV file and returns `(audio_data, samplerate)`.

#### `pst.save_wav(path, audio_data, samplerate)`
Saves a NumPy array to a WAV file.

#### `pst.record_and_save_wav(duration=3, rate=44100, channels=1, directory=None)`
Records audio and saves it as a WAV file in a new session folder.

#### `pst.batch_process_wavs(directory)`
Loads, normalizes, trims, and generates spectrograms for all WAV files in a directory.

#### `pst.normalize_audio(audio_data)`
Normalizes audio data to the range [-1, 1].

#### `pst.trim_silence(audio_data, threshold=0.01)`
Removes leading and trailing silence from audio data.

#### `pst.to_mono(audio_data)` / `pst.to_stereo(audio_data)`
Converts audio data between mono and stereo formats.

### Storage utilities

#### `pst.get_folder_size(directory=None)`
Returns folder size in bytes.

#### `pst.print_folder_size(directory=None)`
Prints the total size of the latest session folder.

## Common errors and fixes

- **No audio input device available**
  - Ensure your OS microphone permissions are enabled.
  - Verify input devices with your system audio settings.

- **Permission denied when creating folders**
  - Pass a writable path to `create_session_folder(directory=...)`.

- **Unsupported operating system error**
  - `get_default_directory()` supports Windows, macOS, and Linux only.

## Development

Run tests:

```bash
pytest
```

Test layout:
- `tests/test_spectrogram.py`: behavior of the library.
- `tests/test_audio_processing.py`: tests for audio utility functions.
- `tests/test_wav_io.py`: tests for WAV file input/output and processing.
- `tests/test_versioning.py`: release version bump rules.
- `tests/test_packaging_metadata.py`: packaging/version source-of-truth checks.

## Examples

You can find examples in the `examples/` directory:

- `examples/basic_workflow.py`: Basic script, same as in quickstart.
- `examples/record_duration.py`: Records and saves for a specified duration.
- `examples/record_infinite.py`: Infinitely records and saves spectrograms in a loop.
- `examples/load_wav.py`: Shows how to load a WAV and plot its spectrogram.
- `examples/batch_processing.py`: Demonstrates batch processing of multiple WAV files.

## Contributing

Contributions are welcome.

## License

This project is licensed under the General Public License. See `LICENSE` for details.
