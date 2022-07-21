from __future__ import annotations

from abc import ABC, abstractmethod


# Procedural code will work with Context.
# Behavior defined in classes implementing State


class State(ABC):
    # do not try and pass context in here this is just
    # to initialize the variable. State must not
    def __init__(self):
        self._context = None

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context) -> None:
        self._context = context

    def get(self, key):
        return self._context.get(key)

    def set(self, key, value):
        return self._context.set(key, value)

    @abstractmethod
    def action(self) -> None:
        # self.context.transition(NextState())
        pass
