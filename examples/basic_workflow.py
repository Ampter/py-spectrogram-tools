import pyspectools2 as pst

session_folder = pst.create_session_folder()
audio_data = pst.record_audio(duration=5)
fig, _ = pst.plot_spectrogram(audio_data)
output_file = pst.save_spectrogram(fig, session_folder)

print(f"Saved spectrogram: {output_file}")
