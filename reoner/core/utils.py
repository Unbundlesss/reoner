import logging
import re
from decimal import Decimal, getcontext
from typing import Union, Literal
from pydub import AudioSegment
from pydub.utils import mediainfo


def extract_bpm(name: str) -> Union[Decimal, Literal[False]]:
    logging.debug('getting from filename')
    valid = re.compile(r"\W(\d{2,3}(?:\.\d{1,10})?)BPM\W")
    try:
        match = valid.search(name).group(1)
        return Decimal(match)
    except AttributeError:
        logging.debug('getting from filename failed')
        return False


class MediaInfo:
    def __init__(self, filename, bpm):
        self.fp32nd = None
        self.total32nds = None
        self.beat32nd = None
        self.beat_length = None
        self.duration = None
        self.duration_ts = None
        self.filename = filename
        self.bpm = bpm
        getcontext().prec = 4
        logging.debug(f"file is: {filename}")
        info = mediainfo(filename)
        logging.debug(info)
        self.duration_ts = Decimal(str(info["duration_ts"]))
        self.duration = Decimal(str(info["duration"]))
        self.beat_length = Decimal(60 / bpm)
        logging.debug(f"beat length: {self.beat_length}")
        self.beat32nd = Decimal(self.beat_length / 8)
        logging.debug(f"32nd length: {self.beat32nd}")
        self.total32nds = Decimal(self.duration / self.beat32nd)
        logging.debug(f"total 32nds: {self.total32nds}")
        self.fp32nd = Decimal(self.duration_ts / self.total32nds)
        logging.debug(f"frames per 32nd: {self.fp32nd}")

    @staticmethod
    def make(filename):
        """For the sake of simplicity here, lets start with the
        assumption that we always pull the bpm from the filename"""
        bpm = extract_bpm(filename)
        if bpm:
            logging.debug(f"found bpm: {bpm}")
            mediainfo = MediaInfo(filename, bpm)
            return mediainfo

        return False


def chonk(segment: AudioSegment, media_info: MediaInfo, offset: int) -> AudioSegment:
    logging.debug('Slicing sample')
    end = int(segment.frame_count())
    start = int(offset * media_info.fp32nd)

    logging.debug(f'seg 1 {start} - {end}')
    logging.debug(f'seg 2 {0} - {start - 1}')
    # TODO: Fix modulo
    slice1 = segment.get_sample_slice(start, end)
    slice2 = segment.get_sample_slice(0, start - 1)
    return slice1 + slice2
