import argparse
import logging
from decimal import Decimal
from ..core.reone import reone_directory
from .interactive import choose_file, choose_offset
from ..core.pather import Pather
from ..core.reoneablemedia import ReoneableMedia


def main():
    parser = argparse.ArgumentParser(description="Re-one your rifffs.")
    parser.add_argument("file", type=str, help="Path to input file.", nargs="?")
    parser.add_argument(
        "--outpath",
        type=Pather.arg_type,
        required=False,
        help="Directory where to output files.",
    )

    parser.add_argument(
        "--bpm",
        type=Decimal,
        required=False,
        help="manually specify bpm, up to 4 digits of precision, ie 87.1234",
    )

    parser.add_argument(
        "--directory",
        action="store_true",
        required=False,
        help="Specify that the path entered is a directory.",
    )

    parser.add_argument(
        "--offset",
        type=int,
        required=False,
        help="The number of 32nds you want to offset by.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        required=False,
        help="Output a lot of debug info.",
    )
    args = parser.parse_args()

    if args.verbose is True:
        logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)

    logging.debug(args)

    if args.directory is True:
        if args.offset is None:
            logging.error("--directory requires --offset to be specified")
            return

        reone_directory(args.file, args.offset)
        return

    if args.file is None:
        # start file chooser dialog
        sound_file = choose_file()
    else:
        sound_file = args.file

    if not sound_file:
        logging.error("I can't figure out the file, sorry.")
        return

    bpm = None
    if args.bpm is not None:
        logging.debug("getting bpm from --bpm")
        bpm = args.bpm

    if bpm:
        seg = ReoneableMedia(sound_file, bpm=bpm)
    else:
        seg = ReoneableMedia(sound_file)

    if args.offset is None:
        offset = choose_offset(seg)
    else:
        offset = args.offset

    if offset is False:
        logging.error("Quit")
        return

    seg.offset = offset

    if args.outpath is not None:
        logging.debug("getting outpath from --outpath")
        seg.outpath = args.outpath
    else:
        logging.debug("using in path as outpath")

    seg.save()
