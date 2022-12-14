from typing import Union
from ..core.state import Context


class ReonerCliContext(Context):
    def __init__(self, state, options: Union[dict, None]):
        # set the default props here,
        # but leave arg processing to the state.
        props = {
                "verbose": False,
                "directory": False,
                "offset": None,
                "file": None,
                "bpm": None,
                "outpath": None
        }

        if props is not None:
            # mutates dict directly
            props.update(options)

        super().__init__(state, props)
