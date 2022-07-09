import argparse
import logging
import os
from decimal import Decimal
from .. core.reone import reone


from reoner.cli.interactive import choose_file, choose_offset
from reoner.core.pather import Pather
from reoner.core.utils import extract_bpm, MediaInfo


def main():
    parser = argparse.ArgumentParser(description="Re-one your rifffs.")
    parser.add_argument(
        "file",
        type=str,
        help="Path to input file.",
        nargs="?"
    )
    parser.add_argument(
        "--outpath",
        type=Pather.arg_type,
        required=False,
        help="Directory where to output files."
    )
    parser.add_argument(
        "--bpm",
        type=Decimal,
        required=False,
        help="manually specify bpm, up to 4 digits of precision, ie 87.1234",
    )
    parser.add_argument(
        "--offset",
        type=int,
        required=False,
        help="The number of 32nds you want to offset by.",
    )
    parser.add_argument("--verbose", action="store_true", required=False, help="Output a lot of debug info.")
    args = parser.parse_args()

    if args.verbose is True:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    logging.debug(args)

    if args.file is None:
        # start file chooser dialog
        sound_file = choose_file()
    else:
        sound_file = args.file

    if not sound_file:
        logging.error("I can't figure out the file, sorry.")
        return

    if args.bpm is None:
        bpm = extract_bpm(sound_file)
    else:
        logging.debug("getting bpm from --bpm")
        bpm = args.bpm

    if not bpm:
        logging.error("I need the bpm either in the filename or in --bpm.")
        return

    media_info = MediaInfo(sound_file, bpm)

    if args.offset is None:
        offset = choose_offset(sound_file, bpm, media_info)
    else:
        offset = args.offset

    if offset is False:
        logging.error('Quit')
        return

    segment = reone(sound_file, bpm, offset, media_info)

    if not segment:
        logging.error('No file')
        return

    root, ext = os.path.splitext(os.path.basename(sound_file))
    if args.outpath is not None:
        logging.debug("getting outpath from --outpath")
        out = Pather(args.outpath)
    else:
        logging.debug("using in path as outpath")
        out = Pather(sound_file)

    final_path = f"{out}/{root}.wav"

    with open(final_path, "wb") as outfile:
        segment.export(outfile, format="wav")
        print(f"File written to {final_path}")
