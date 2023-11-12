from contextlib import contextmanager
import logging
import os
import re
from decimal import getcontext, Decimal
from typing import Union, Literal

from pydub import AudioSegment
from pydub.playback import play as mediaplay
from pydub.utils import mediainfo
from pydub.playback import _play_with_simpleaudio
from .pather import Pather, PatherFile

class ReoneableMedia:
    def __init__(self, filename, **kwargs):
        # filename = kwargs.get("filename", False)
        self._bpm = 0.0000

        self.beat_length = None
        self.beat32nd = None
        self.total32nds = None
        self.fp32nd = None
        self.playhandler = None

        if not os.path.isfile(filename):
            error = f"file not a file: {filename}"
            logging.error(error)
            raise AttributeError(error)

        self._offset = int(kwargs.get("offset", 0))
        bpm = kwargs.get("bpm", False)

        if not bpm:
            bpm = self._bpm = self.extract_bpm(filename)

        if bpm:
            logging.debug(f"found bpm: {bpm}")
            self._bpm = bpm
        else:
            error = f"bpm not supplied or cannot extract bpm: {filename}"
            logging.error(error)
            raise AttributeError(error)

        self.floatBpm = self._bpm / 60

        # set the filename based on the existing one
        root, ext = os.path.splitext(os.path.basename(filename))
        self._outname = f"{root}.wav"
        self._outpath = os.path.dirname(filename)
        with open(filename, "rb") as sound:
            segment = AudioSegment.from_file(sound)

        logging.debug(f"file is: {filename}")

        # keep original segment separately
        self.original_segment = segment
        self.current_segment = segment
        self.filename = filename

        getcontext().prec = 4

        self.info = mediainfo(filename)
        logging.debug(self.info)

        # duration as frames
        self.duration_ts = Decimal(str(self.info["duration_ts"]))

        # duration as time
        self.duration = Decimal(str(self.info["duration"]))

        self._calculate_lengths()

    @property
    def stem(self):
        return self.current_segment

    @property
    def bpm(self):
        return self._bpm

    @bpm.setter
    def bpm(self, value):
        self._bpm = value
        self._calculate_lengths()

    def _calculate_lengths(self):
        bpm = self._bpm
        # A beat (as in beats per minute) is a quarter note.
        self.beat_length = Decimal(60 / bpm)
        logging.debug(f"beat length: {self.beat_length}")
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

    @staticmethod
    def extract_bpm(name: str) -> Union[Decimal, Literal[False]]:
        logging.debug("getting from filename")
        valid = re.compile(r"\b(\d{2,3}(?:\.\d{1,10})?)BPM\b", re.I)
        try:
            match = valid.search(name).group(1)
            return Decimal(match)
        except AttributeError:
            logging.debug("getting from filename failed")
            return False

    @property
    def outpath(self):
        """The directory to put out into"""
        return self._outpath

    @outpath.setter
    def outpath(self, path):
        self._outpath = Pather(path)

    @property
    def outname(self):
        return self._outname

    @outname.setter
    def outname(self, name):
        """The name of the output file"""
        self._outname = name

    @property
    def finalfile(self):
        return PatherFile(self._outpath, self._outname)

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        # TODO some kind of validation
        self._offset = int(value)
        normalized = self._offset % self.total32nds

        end = int(self.original_segment.frame_count())

        start = int(normalized * self.fp32nd)

        logging.debug(f"seg 1 {start} - {end}")
        logging.debug(f"seg 2 {0} - {start - 1}")

        # re-assemble the loop
        slice1 = self.original_segment.get_sample_slice(start, end)
        slice2 = self.original_segment.get_sample_slice(0, start - 1)
        self.current_segment = slice1 + slice2

    def play(self):
        self.stop()
        self.playhandler = _play_with_simpleaudio(self.current_segment)
        # mediaplay(self.current_segment)

    def preview(self):
        self.stop()
        """Play first two seconds"""
        seg = self.current_segment[0:2000]
        self.playhandler = _play_with_simpleaudio(seg)

    def stop(self):
        if self.playhandler is not None and self.playhandler.is_playing():
            self.playhandler.stop()

    @contextmanager
    def writebin(self):
        name = self.finalfile
        try:
            f = open(name, "wb")
            yield (f, name)
        finally:
            f.close()

    def save(self):
        # final name updated automatically
        with self.writebin() as (stream, filename):
            self.current_segment.export(stream, format="wav")
            print(f"File written to {filename}")
