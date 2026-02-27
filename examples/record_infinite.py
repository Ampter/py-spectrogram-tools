import pyspectools2 as pst
import sys
import time

def main():
    print("Infinite recording mode started. Press Ctrl+C to stop.")
    try:
        # Create a base folder for this infinite session
        session_folder = pst.create_session_folder()

        while True:
            print(f"\n[{time.ctime()}] Recording 5 seconds...")
            audio_data = pst.record_audio(duration=5)

            print("Generating spectrogram...")
            fig, _ = pst.plot_spectrogram(audio_data)
            output_file = pst.save_spectrogram(fig, session_folder)

            print(f"Saved: {output_file}")

    except KeyboardInterrupt:
        print("\nStopping infinite recording...")
        pst.print_folder_size()
        sys.exit(0)

if __name__ == '__main__':
    main()
