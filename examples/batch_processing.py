import pyspectools2 as pst
import os
import tempfile
import numpy as np

def main():
    # Create a temporary directory with some dummy WAV files for demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Creating dummy WAV files in {temp_dir}...")

        for i in range(3):
            path = os.path.join(temp_dir, f"sample_{i}.wav")
            # Generate some noise
            data = np.random.uniform(-0.5, 0.5, 44100)
            pst.save_wav(path, data, 44100)

        print("Starting batch processing...")
        # batch_process_wavs will create a new session and save spectrograms there
        pst.batch_process_wavs(temp_dir)

        latest_session = pst.get_latest_session_folder()
        print(f"Batch processing complete. Results saved in: {latest_session}")
        pst.print_folder_size()

if __name__ == "__main__":
    main()
