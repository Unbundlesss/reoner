import logging
import re
from decimal import Decimal, getcontext
from typing import Union, Literal
from pydub import AudioSegment
from pydub.utils import mediainfo
import os

from . pather import Pather


def extract_bpm(name: str) -> Union[Decimal, Literal[False]]:
    logging.debug('getting from filename')
    valid = re.compile(r"\W(\d{2,3}(?:\.\d{1,10})?)BPM\W")
    try:
        match = valid.search(name).group(1)
        return Decimal(match)
    except AttributeError:
        logging.debug('getting from filename failed')
        return False


def get_files(path):
    opts = os.listdir(path)
    # return a list of
    opts = [{
                "name": f'{i}/',
                "value": i
            } if os.path.isdir(i) else i for i in opts if os.path.isdir(i) or i.endswith('.aiff')]
    # filter out hidden files
    opts = filter(lambda x: not x['name'].startswith('.') if isinstance(x, dict) else not x.startswith('.'), opts)
    # sort files
    opts = sorted(opts, key=lambda x: x['name'] if isinstance(x, dict) else x)

    return opts


def get_files_full_paths(path):
    path = os.path.abspath(os.path.realpath(path))
    listem = os.listdir(path)
    opts = [f"{path}/{i}" if os.path.isfile(f"{path}/{i}") else None for i in listem if i.endswith('.aiff')]
    opts = filter(lambda x: x is not None and not x.startswith('.'), opts)
    # cast as list otherwise it's an iterable
    opts = list(opts)
    logging.debug(opts)
    return opts


class MediaInfo:
    def __init__(self, filename, **kwargs):
        # filename = kwargs.get("filename", False)

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

        # set the filename based on the existing one
        root, ext = os.path.splitext(os.path.basename(filename))
        self.out_name = f"{root}.wav"
        self.out_path = ''
        self.final_name = ''

        with open(filename, "rb") as sound:
            segment = AudioSegment.from_file(sound)

        logging.debug(f"file is: {filename}")
        # confusingly I used the same name mediainfo.
        self.original_segment = segment
        self.current_segment = segment
        self.filename = filename
        self.set_outpath(filename)
        self.offset = kwargs.get("offset", 0)
        getcontext().prec = 4
        self.info = mediainfo(filename)
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
        self.out_path = Pather(path)
        self.final_name = f"{self.out_path}/{self.out_name}"

    def reone(self):
        logging.debug('Slicing sample')
        end = int(self.original_segment.frame_count())
        start = int(self.offset * self.fp32nd)

        logging.debug(f'seg 1 {start} - {end}')
        logging.debug(f'seg 2 {0} - {start - 1}')
        # TODO: Fix modulo
        slice1 = self.original_segment.get_sample_slice(start, end)
        slice2 = self.original_segment.get_sample_slice(0, start - 1)
        self.current_segment = slice1 + slice2
        return self.current_segment

    def set_offset(self, offset):
        self.offset = offset

    def save(self):
        logging.debug(f"Save target is {self.final_name}")
        with open(self.final_name, "wb") as outfile:
            self.current_segment.export(outfile, format="wav")
            print(f"File written to {self.final_name}")

