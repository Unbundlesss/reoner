from typing import Union, Literal
from .pather import Pather
from decimal import getcontext, Decimal
from pydub import AudioSegment
from pydub.utils import mediainfo
import re
import logging


def find_32nd_details(loop: str, bpm: Decimal) -> [Decimal, Decimal]:
    getcontext().prec = 4
    logging.debug(f"file is: {loop}")
    info = mediainfo(loop)
    logging.debug(info)
    duration_ts = Decimal(str(info["duration_ts"]))
    duration = Decimal(str(info["duration"]))

    beat_length = Decimal(60 / bpm)
    logging.debug(f"beat length: {beat_length}")
    beat32nd = Decimal(beat_length / 8)
    logging.debug(f"32nd length: {beat32nd}")
    total32nds = Decimal(duration / beat32nd)
    logging.debug(f"total 32nds: {total32nds}")
    fp32nd = Decimal(duration_ts / total32nds)
    logging.debug(f"frames per 32nd: {fp32nd}")
    return [fp32nd, total32nds]


def extract_bpm(name: str) -> Union[Decimal, Literal[False]]:
    logging.debug('getting from filename')
    valid = re.compile(r"\W(\d{2,3}(?:\.\d{1,10})?)BPM\W")
    try:
        match = valid.search(name).group(1)
        return Decimal(match)
    except AttributeError:
        logging.debug('getting from filename failed')
        return False


def chonk(segment: AudioSegment, fp32nd: Union[int, Decimal], offset: int) -> AudioSegment:
    logging.debug('Slicing sample')
    end = int(segment.frame_count())
    start = int(offset * fp32nd)
    slice1 = segment.get_sample_slice(start, end)
    slice2 = segment.get_sample_slice(0, start - 1)
    return slice1 + slice2
