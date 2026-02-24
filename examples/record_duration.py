import pyspectools2 as pst
import sys


def main(seconds=10):
    try:
        # 1. Create a timestamped folder for this session
        session_folder = pst.create_session_folder()
        print(f"Session created at: {session_folder}")

        # 2. Record audio for the specified duration
        print(
            f"Recording for {seconds} seconds... (Press Ctrl+C to stop early)")
        audio_data = pst.record_audio(duration=seconds)

        # 3. Generate and save the visualization
        print("Processing spectrogram...")
        fig, _ = pst.plot_spectrogram(audio_data)
        output_path = pst.save_spectrogram(fig, session_folder)

        print(f"Success! Spectrogram saved to: {output_path}")

    except KeyboardInterrupt:
        print("\nRecording cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    # You can change the duration here (e.g., 30 for thirty seconds)
    main(seconds=5)
