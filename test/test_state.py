# from reoner.cli import ReonerCliContext, InitialState
from reoner.cli import ReonerCliContext
from reoner.core.state import State, Context, FinishedState
import pytest


class Handlers:
    def __init__(self):
        self.called = []

    def __getattr__(self, name):
        def func():
            self.called.append(name)

        return func


@pytest.fixture
def handlers():
    return Handlers()


def test_state_and_context():
    state = State('Success')
    ctx = Context(state)
    assert ctx.state_result == 'Success'
    assert ctx.state == 'State'
    ctx.set('key', 'value1')
    assert ctx.get('key') == 'value1'


def test_state_transition(handlers):
    class DummyState(State):
        def action(self):
            handlers.action_test1()
            self.context.transition(DummyState2())

    class DummyState2(State):
        def action(self):
            handlers.action_test2()
            self.context.transition(FinishedState('success'))

    ctx = Context(DummyState())
    assert ctx.state == 'DummyState'

    ctx.action()
    assert ctx.state == 'DummyState2'

    ctx.action()
    assert ctx.state == 'FinishedState'
    assert handlers.called == ['action_test1', 'action_test2']

    assert ctx.state_result == 'success'


def test_cli_context():
    state1 = State('Success1')
    options = {
        "verbose": True,
        "offset": None,
        "file": 'test.aiff',
        "bpm": 123.00,
        "outpath": None
    }
    ctx = ReonerCliContext(state1, options)
    assert not ctx.get('directory')
    assert ctx.get('bpm') == 123.00
    assert ctx.get('verbose')

# def test_context():
#     ctx = ReonerCliContext(InitialState(), None)
#     while ctx.get_state != "FinishedState":
#         ctx.action()
