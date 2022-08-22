import logging
import re
from decimal import Decimal, getcontext
from typing import Union, Literal
from pydub import AudioSegment
from pydub.playback import play as mediaplay
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

        # keep original segment separately
        self.original_segment = segment
        self.current_segment = segment
        self.filename = filename
        self.set_outpath(filename)

        getcontext().prec = 4

        self.info = mediainfo(filename)
        logging.debug(self.info)

        # duration as time
        self.duration_ts = Decimal(str(self.info["duration_ts"]))

        # duration as frames
        self.duration = Decimal(str(self.info["duration"]))

        # A beat (as in beats per minute) is a quarter note.
        self.beat_length = Decimal(60 / bpm)
        logging.debug(f"beat length: {self.beat_length}")

        # Each offset is equal to a 32nd note.
        self.offset = kwargs.get("offset", 0)

        # A 32nd note is an eighth of a beat.
        # A beat has 4 16ths. There are 2 32nds in a 16th.
        self.beat32nd = Decimal(self.beat_length / 8)
        logging.debug(f"32nd length: {self.beat32nd}")

        # The total length of the stem in 32nd notes
        self.total32nds = Decimal(self.duration / self.beat32nd)
        logging.debug(f"total 32nds: {self.total32nds}")

        # And now find the total number of frames per 32nd note
        self.fp32nd = Decimal(self.duration_ts / self.total32nds)
        logging.debug(f"frames per 32nd: {self.fp32nd}")

    def set_outpath(self, path):
        self.out_path = Pather(path)
        self.final_name = f"{self.out_path}/{self.out_name}"
        return self.final_name

    def reone(self, offset=None):
        logging.debug('Slicing sample')

        # allow overshooting the length of the sample.
        # This is needed in the case of an offset being
        # calculated on a longer loop than this one.
        if offset is None:
            input = self.offset % self.total32nds
        else:
            input = self.set_offset(offset) % self.total32nds

        end = int(self.original_segment.frame_count())
        start = int(input * self.fp32nd)

        logging.debug(f'seg 1 {start} - {end}')
        logging.debug(f'seg 2 {0} - {start - 1}')

        # re-assemble the loop
        slice1 = self.original_segment.get_sample_slice(start, end)
        slice2 = self.original_segment.get_sample_slice(0, start - 1)
        self.current_segment = slice1 + slice2
        return self.current_segment

    def set_offset(self, offset):
        # TODO some kind of validation
        self.offset = offset
        return self.offset

    def play(self):
        mediaplay(self.current_segment)

    def preview(self):
        """Play first two seconds"""
        seg = self.current_segment[0:2000]
        mediaplay(seg)

    def save(self, outpath=None):
        if outpath is None:
            filename = self.final_name
        else:
            filename = self.set_outpath(outpath)
        logging.debug(f"Save target is {filename}")
        with open(filename, "wb") as outfile:
            self.current_segment.export(outfile, format="wav")
            print(f"File written to {filename}")
