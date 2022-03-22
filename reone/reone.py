import logging
import os.path

from pydub import AudioSegment

from .mediainfo import MediaInfo
from .utils import chonk

"""
example inputs:
2 - name name - Delay - 28.0616BPM - 2022-02-02-00-23.aiff
2 - name name - Lowpass - 125BPM - 2022-01-17-11-24.aiff
4 - name name - Smudge - 57.1445BPM - 2021-08-13-08-33.aiff
"""

__all__ = ['reone']


def reone(filename, bpm, offset,
          media_info: MediaInfo = None):
    if not os.path.isfile(filename):
        logging.error(f"file not a file: {filename}")
        return False

    if media_info is None:
        media_info = MediaInfo(filename, bpm)

    if not media_info.fp32nd:
        logging.debug("Could not determine the frames per 32nd beat.")
        return False

    with open(filename, "rb") as sound:
        segment = AudioSegment.from_file(sound)

    adjusted: AudioSegment = chonk(segment, media_info, offset)

    return adjusted
