import logging
import os.path

from pydub import AudioSegment
from .utils import find_32nd_details, chonk

"""
example inputs:
2 - name name - Delay - 28.0616BPM - 2022-02-02-00-23.aiff
2 - name name - Lowpass - 125BPM - 2022-01-17-11-24.aiff
4 - name name - Smudge - 57.1445BPM - 2021-08-13-08-33.aiff
"""


def reone(filename, bpm, offset, media32nds=False):
    if not os.path.isfile(filename):
        logging.error(f"file not a file: {filename}")
        return False

    """this gets a bit messy"""
    if media32nds is False:
        [fp32nd, total32nds] = find_32nd_details(filename, bpm)
    else:
        [fp32nd, total32nds] = media32nds

    if not fp32nd:
        logging.debug("Could not determine the frames per 32nd beat.")
        return False

    with open(filename, "rb") as sound:
        segment = AudioSegment.from_file(sound)

    adjusted: AudioSegment = chonk(segment, fp32nd, offset)

    return adjusted
