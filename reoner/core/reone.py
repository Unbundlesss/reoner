import logging
import os.path

from . utils import ReoneableMedia, get_files_full_paths

"""
example inputs:
2 - name name - Delay - 28.0616BPM - 2022-02-02-00-23.aiff
2 - name name - Lowpass - 125BPM - 2022-01-17-11-24.aiff
4 - name name - Smudge - 57.1445BPM - 2021-08-13-08-33.aiff
"""

__all__ = ['reone', 'reone_directory', 'reone_multiple']


def reone(filename, offset):
    media = ReoneableMedia(filename, offset=offset)
    media.reone()
    return media


def reone_directory(path, offset):
    logging.debug(f"Begin re-oneing of {path}")
    files = get_files_full_paths(path)
    reone_multiple(files, offset)


def reone_multiple(filelist, offset):
    logging.debug(f"Re-oneing {len(filelist)} files.")
    for i in filelist:
        # current = ReoneableMedia(i)
        logging.debug(f"File {i}")
        media = ReoneableMedia(i)
        media.set_offset(offset)
        media.reone()
        media.save()
