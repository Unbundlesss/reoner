from .core.reoneablemedia import ReoneableMedia
from .cli.cli import main as reone

def from_file(filename):
    return ReoneableMedia(filename)


__all__ = [
    'reone',
    'from_file'
    'ReoneableMedia'
]
