import logging
import os.path

from .utils import MediaInfo

"""
example inputs:
2 - name name - Delay - 28.0616BPM - 2022-02-02-00-23.aiff
2 - name name - Lowpass - 125BPM - 2022-01-17-11-24.aiff
4 - name name - Smudge - 57.1445BPM - 2021-08-13-08-33.aiff
"""

__all__ = ['reone']


def reone(filename, offset):
    media = MediaInfo(filename=filename, offset=offset)
    media.reone()
    return media.current_segment


def reone_multiple(filelist, bpm, offset):
    logging.debug(f"Re-oneing {len(filelist)} files.")
    for i in filelist:
        # current = MediaInfo(i)
        logging.debug(f"File {i}")
        media = MediaInfo(i,)
        result = reone(i, bpm, offset)
