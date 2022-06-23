import logging
from decimal import getcontext, Decimal
from pydub.utils import mediainfo
from . utils import extract_bpm


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
