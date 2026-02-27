import pyspectools2 as pst

wav_path = "yourfile.wav"  # change this
fig, ax, outfile = pst.load_and_plot_wav(wav_path)
print(f"Saved spectrogram from WAV: {outfile}")
