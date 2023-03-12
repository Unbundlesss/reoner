from __future__ import annotations

from abc import ABC, abstractmethod
# Procedural code will work with Context.
#

from typing import Optional, Union, TypeVar

T = TypeVar("T")


class State(ABC):
    """
    Generally, the context is specific to a set of states and carries
    the data that the states operate on.

    State is a set of behaviors or side effects; its action method
    determines the starting behavior. The state may also react to events.
    Ultimately, the state decides when to transition.

    A transition is the act of a context swapping out its current state for another.

    At the end of each transition, the context calls the states' action method
    to initialize the state and its behavior.

    States should extend this class and contexts should extend Context.
    """

    def __init__(self, state_result: str = 'No result'):
        self.state_result = state_result
        self._context = None

    @property
    def context(self) -> Union[Context, None]:
        return self._context

    @context.setter
    def context(self, context: Context) -> None:
        self._context = context

    def get(self, key: str) -> Context:
        return self._context.get(key)

    def set(self, key: str, value: T) -> T:
        return self._context.set(key, value)

    @property
    def ui(self):
        return self._context.ui

    @ui.setter
    def ui(self, ui):
        self._context.ui = ui

    def action(self) -> None:
        pass


class FinishedState(State):
    """Utility state"""
    pass


class Context:
    def __init__(self, initial_state: State, props: Optional[dict] = None) -> None:
        if props is None:
            props = {}
        self._inner_props = {}
        self._user_props = props
        self._state = initial_state
        self._ui = None
        self._state.context = self

    def get(self, key: str):
        if key in self._user_props:
            return self._user_props[key]
        else:
            return None

    def set(self, key: str, value: T) -> None:
        self._user_props[key] = value

    @property
    def ui(self):
        return self._ui

    @ui.setter
    def ui(self, ui) -> None:
        self._ui = ui

    @property
    def state_result(self):
        return self._state.state_result

    @property
    def state(self) -> str:
        return type(self._state).__name__

    def transition(self, state: State) -> None:
        """
        It is tempting to call action() from here.
        But then the states would be calling each other
        """
        self._state = state
        self._state.context = self

    # Proxy method to the main action of the state.
    # To be run only by the top level function such as main()
    def action(self) -> None:
        self._state.action()
