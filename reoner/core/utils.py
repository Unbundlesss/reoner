import logging
import re
from decimal import Decimal, getcontext
from typing import Union, Literal
from pydub import AudioSegment
from pydub.utils import mediainfo
import os

from .pather import Pather


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

    logging.debug(f'seg 1 {start} - {end}')
    logging.debug(f'seg 2 {0} - {start - 1}')
    # TODO: Fix modulo
    slice1 = segment.get_sample_slice(start, end)
    slice2 = segment.get_sample_slice(0, start - 1)
    return slice1 + slice2


class MediaInfo:
    def __init__(self, *args, **kwargs):
        filename = kwargs.get("filename", False)

        if not os.path.isfile(filename):
            error = f"file not a file: {filename}"
            logging.error(error)
            raise AttributeError(error)

        bpm = kwargs.get("bpm", False)

        if not bpm:
            bpm = extract_bpm(filename)
        if bpm:
            logging.debug(f"found bpm: {bpm}")
            self.bpm = bpm
        else:
            error = f"bpm not supplied or cannot extract bpm: {filename}"
            logging.error(error)
            raise AttributeError(error)

        with open(filename, "rb") as sound:
            segment = AudioSegment.from_file(sound)

        self.original_segment = segment
        self.current_segment = segment
        self.fp32nd = None
        self.total32nds = None
        self.beat32nd = None
        self.beat_length = None
        self.duration = None
        self.duration_ts = None
        self.filename = filename
        self.offset = kwargs.get("offset", 0)
        getcontext().prec = 4
        logging.debug(f"file is: {filename}")
        # confusingly I used the same name mediainfo.
        self.info = mediainfo(filename)
        self.outpath = Pather(filename)
        logging.debug(self.info)
        self.duration_ts = Decimal(str(self.info["duration_ts"]))
        self.duration = Decimal(str(self.info["duration"]))
        self.beat_length = Decimal(60 / bpm)
        logging.debug(f"beat length: {self.beat_length}")
        self.beat32nd = Decimal(self.beat_length / 8)
        logging.debug(f"32nd length: {self.beat32nd}")
        self.total32nds = Decimal(self.duration / self.beat32nd)
        logging.debug(f"total 32nds: {self.total32nds}")
        self.fp32nd = Decimal(self.duration_ts / self.total32nds)
        logging.debug(f"frames per 32nd: {self.fp32nd}")

    def set_outpath(self, path):
        root, ext = os.path.splitext(os.path.basename(path))
        self.outpath = Pather(path)
        final_path = f"{out}/{root}.wav"

        with open(final_path, "wb") as outfile:
            segment.export(outfile, format="wav")
            print(f"File written to {final_path}")

    def reone(self):
        adjusted: AudioSegment = chonk(self.original_segment, self.info, self.offset)
        self.current_segment = adjusted
        return True

    def set_offset(self, offset):
        self.offset = offset
