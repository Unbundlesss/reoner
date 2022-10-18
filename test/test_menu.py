# from reoner.cli import ReonerCliContext, InitialState
import pytest
from reoner.cli import ReonerCliContext
from reoner.cli.interactive import generate_menu_layout
from reoner.core.state import State, Context
from reoner.cli.items import MenuItem
from prompt_toolkit.application import Application
from prompt_toolkit.application.current import set_app
from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPress, KeyProcessor
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Layout, Window
from prompt_toolkit.output import DummyOutput
from reoner.cli.menu import Menu, transform_line, StatusBar, MenuColorizer
from contextlib import contextmanager
import textwrap


class Handlers:
    def __init__(self):
        self.called = []

    def __getattr__(self, name):
        def func(event):
            self.called.append(name)

        return func


@pytest.fixture
def handlers():
    return Handlers()


def test_menu_items(mocker):
    menu = Menu(header='Test Header',
                options=[('Quit', 'q', 'Exit quietly.'), ('Help', 'h', 'Get help.')])

    menu.layout = generate_menu_layout(menu)

    assert menu.total_lines == 3
    assert menu.total_focusable_items == 2

    result = textwrap.dedent("""\
    Test Header
    Quit
    Help""")

    assert textwrap.dedent(menu.get_text()) == result

    menu.jump_selection(1)
    assert menu.pos == 1