from __future__ import annotations

from typing import Optional, Union

from reoner.core.state import State


class Context:
    _state = None

    def __init__(self, initial_state: State, props: Optional[dict] = None) -> None:
        if props is None:
            props = {}
        self._context_props = props
        self._state = initial_state
        self._state.context = self

    def get(self, key):
        if key in self._context_props:
            return self._context_props[key]
        else:
            return None

    def set(self, key, value):
        self._context_props[key] = value
        return value

    def get_state(self):
        return type(self._state).__name__

    def transition(self, state: State):
        self._state = state
        self._state.context = self

    # Proxy method to the main action of the state.
    # To be run only by the top level function such as main()
    def action(self):
        self._state.action()


class ReonerCliContext(Context):
    def __init__(self, state, options: Union[dict, None]):
        # set the default props here,
        # but leave arg processing to the state.
        props = {
            "options": {
                "verbose": False,
                "directory": False,
                "offset": None,
                "file": None,
                "bpm": None,
                "outpath": None
            }}

        if options is not None:
            # mutates dict directly
            props['options'].update(options)

        super().__init__(state, props)
