import logging
import re
from decimal import Decimal
from typing import Union, Literal

from pydub import AudioSegment

from .mediainfo import MediaInfo


def extract_bpm(name: str) -> Union[Decimal, Literal[False]]:
    logging.debug('getting from filename')
    valid = re.compile(r"\W(\d{2,3}(?:\.\d{1,10})?)BPM\W")
    try:
        match = valid.search(name).group(1)
        return Decimal(match)
    except AttributeError:
        logging.debug('getting from filename failed')
        return False


def chonk(segment: AudioSegment, media_info: MediaInfo, offset: int) -> AudioSegment:
    logging.debug('Slicing sample')
    end = int(segment.frame_count())
    start = int(offset * media_info.fp32nd)
    slice1 = segment.get_sample_slice(start, end)
    slice2 = segment.get_sample_slice(0, start - 1)
    return slice1 + slice2
