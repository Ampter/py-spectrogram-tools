# Spectrogram Recorder Library

A Python library for recording audio, generating spectrograms, and managing session data.

## Features

- Record audio from your default input device (`sounddevice`).
- Plot and save spectrograms (`matplotlib`).
- Create numbered session folders (`session_1`, `session_2`, ...).
- Delete the latest session and inspect folder sizes.
- Cross-platform default save location based on the current user's home directory.

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

## Dependencies

- numpy
- sounddevice
- matplotlib

## Import

```python
import pyspectools as pst
```

## API

### `pst.get_default_directory()`
Returns the default directory for spectrogram sessions:

- Windows: `C:\Users\<username>\SOUNDS\spectrograms`
- macOS: `/Users/<username>/SOUNDS/spectrograms`
- Linux: `/home/<username>/SOUNDS/spectrograms`

### `pst.create_session_folder(directory=None)`
Creates a new folder such as `session_5` and returns its path.

### `pst.get_latest_session_folder(directory=None)`
Returns the highest numbered session folder path, or `None`.

### `pst.record_audio(duration=3, rate=44100, channels=1)`
Records audio and returns a flattened NumPy array.

### `pst.plot_spectrogram(audio_data, rate=44100)`
Returns `(fig, ax)` for the generated spectrogram.

### `pst.save_spectrogram(fig, session_folder)`
Saves a PNG in the target session folder and returns the output file path.

### `pst.delete_latest_session_folder(directory=None)`
Deletes the latest session folder.

### `pst.get_folder_size(directory=None)`
Returns folder size in bytes.

### `pst.print_folder_size(directory=None)`
Prints the total size of the latest session folder.

## Usage Example

```python
import pyspectools as pst

session_folder = pst.create_session_folder()
audio_data = pst.record_audio(duration=5)
fig, _ = pst.plot_spectrogram(audio_data)
output_file = pst.save_spectrogram(fig, session_folder)

print(f"Saved spectrogram: {output_file}")
```

## Contributing

Contributions are welcome.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
