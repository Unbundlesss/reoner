import os
import sys

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    from pydub import AudioSegment
    base_path = sys._MEIPASS
    ffmpeg = os.path.realpath(os.path.join(base_path,'bin', "ffmpeg"))
    if not os.path.isfile(ffmpeg):
        raise FileNotFoundError(f"ffmpeg not found at {ffmpeg}")
    AudioSegment.ffmpeg = ffmpeg

if __name__ == "__main__":
    from reoner.cli.cli import main
    main()
