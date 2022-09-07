import logging
import os


def get_files(path):
    opts = os.listdir(path)
    # return a list of
    opts = [{
                "name" : f'{i}/',
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
