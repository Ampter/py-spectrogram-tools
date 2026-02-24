import pyspectools2 as pst
import sys

def main():
    try:
        # Create folder and record
        session_folder = pst.create_session_folder()
        print("Recording for 5 seconds... Press Ctrl+C to abort.")
        
        audio_data = pst.record_audio(duration=5)
        
        # Process and save
        fig, _ = pst.plot_spectrogram(audio_data)
        output_file = pst.save_spectrogram(fig, session_folder)
        print(f"Saved spectrogram: {output_file}")
        
    except KeyboardInterrupt:
        print("\n[Interrupted] Stopping script gracefully...")
        sys.exit(0)

if __name__ == '__main__':
    main()

