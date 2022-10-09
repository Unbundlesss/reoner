import logging
from . pather import Pather
from ..cli.interactive import get_files_full_paths
from . reoneablemedia import ReoneableMedia

"""
example inputs:
2 - name name - Delay - 28.0616BPM - 2022-02-02-00-23.aiff
2 - name name - Lowpass - 125BPM - 2022-01-17-11-24.aiff
4 - name name - Smudge - 57.1445BPM - 2021-08-13-08-33.aiff
"""

__all__ = ['reone', 'reone_directory', 'reone_multiple']


def reone(filename, offset):
    media = ReoneableMedia(filename)
    media.offset = offset
    return media


def reone_directory(inpath, offset):
    path = Pather(inpath)
    logging.debug(f"Begin re-oneing of {path}")
    files = get_files_full_paths(path)
    reone_multiple(files, offset)


def reone_multiple(filelist, offset):
    logging.debug(f"Re-oneing {len(filelist)} files.")
    for i in filelist:
        # current = ReoneableMedia(i)
        logging.debug(f"File {i}")
        media = ReoneableMedia(i)
        media.offset = offset
        media.save()
