import glob
import pyspectools2 as pst

for wav_file in glob.glob("*.wav"):
    fig, ax, out = pst.load_and_plot_wav(wav_file)
    print("Saved", out)