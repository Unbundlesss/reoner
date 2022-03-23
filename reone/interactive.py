from enum import Enum

from PyInquirer import prompt
from PyInquirer import style_from_dict
from prompt_toolkit.validation import Validator, ValidationError
from pydub.exceptions import TooManyMissingFrames
from pydub.playback import play
from pygments.token import Token
from regex import regex

from .mediainfo import MediaInfo
from .reone import reone

__all__ = ['choose_offset', 'default_style']

default_style = style_from_dict({
    Token.Separator: '#ansired',
    Token.QuestionMark: '#ansigreen',
    Token.Selected: '#ansiblue',
    Token.Pointer: '#ansiblue bold',
    Token.Instruction: '#ansiyellow',  # default
    Token.Answer: '#ansiyellow bold',
    Token.Question: '#ansiyellow',
}, include_defaults=True)


class States(Enum):
    SUCCESS = "success"
    TOP = "top"
    NUDGING = "nudging"
    PREVIEW = "preview"
    SUCCESS = "success"
    FAIL = "fail"
    CANCEL = "cancel"
    DIRECT = "direct"


class OffsetValidator(Validator):
    def validate(self, document):
        ok = regex.match(r'^\d{0,4}$', document.text)
        if not ok:
            raise ValidationError(
                message='Please enter an integer, from 0-9999',
                cursor_position=len(document.text))  # Move cursor to end


class NudgeMachineContext:
    def __init__(self, media_info: MediaInfo, offset: int = 0):
        self.media_info: MediaInfo = media_info
        self.offset = offset


class NudgeMachine:
    def __init__(self, context: NudgeMachineContext):
        self.context = context
        self.state = States.TOP
        self.segment = None

    def top(self):
        m = self.context.media_info
        print(f"Filename:\n {m.filename}")
        print(f"{m.total32nds // 32} bars long ({m.total32nds} 32nd notes)")
        questions = [{
            'type': 'expand',
            'message': 'what to do?',
            'name': 'top',
            'choices': [
                {
                    'key': 'i',
                    'name': 'Interactively pick offset',
                    'value': 'nudge'
                },
                {
                    'key': 'm',
                    'name': 'Manually enter offset',
                    'value': 'manual'
                },
                {
                    'key': 'q',
                    'name': 'Quit',
                    'value': 'quit'
                }
            ]
        }]
        answers = prompt(questions)
        if answers['top'] == 'i':
            self.transition(States.NUDGING)
        elif answers['top'] == 'm':
            self.transition(States.DIRECT)
        elif answers['top'] == 'q':
            self.transition(States.CANCEL)
            return False
        return True

    def preview(self):
        m = self.context.media_info
        offset = self.context.offset
        try:
            segment = reone(m.filename, m.bpm, offset, m)
            preview = segment[0:2000]
            print('Playing.')
            play(preview)
        except TooManyMissingFrames:
            print('Segment is too short to preview')
        return True

    def nudging(self):
        m = self.context.media_info
        offset = self.context.offset

        print(f"Filename:\n {m.filename}")
        print(f"{m.total32nds // 32} bars long ({m.total32nds} 32nd notes)")
        questions = [{
            "type": "expand",
            "name": "nudge",
            "message": f"Current offset is {offset}.",
            "choices": [{
                "key": "f",
                "name": "+1 bar",
                "value": 32
            }, {
                "key": "d",
                "name": "+1 quarter",
                "value": 8
            }, {
                "key": "s",
                "name": "+1 32nd note",
                "value": 1
            }, {
                "key": "x",
                "name": "-1 32nd note",
                "value": -1
            }, {
                "key": "c",
                "name": "-1 quarter note",
                "value": -8
            }, {
                "key": "v",
                "name": "-1 bar",
                "value": -32
            }, {
                "key": "p",
                "name": f"Preview starting at {offset}",
                "value": "preview"
            }, {
                "key": "y",
                "name": f"Save with loop starting at {offset}",
                "value": "save"
            }, {
                "key": "q",
                "name": f"Quit",
                "value": "quit"
            }],
        }]
        answers = prompt(questions)
        r = answers['nudge_top']
        if r == "quit":
            self.transition(States.CANCEL)
            return False
        elif r == "save":
            self.transition(States.SUCCESS)
            return False
        elif r == "preview":
            self.transition(States.PREVIEW)
            return True
        else:
            self.context.offset += r
            return True

    def direct(self):
        questions = [{
            "type": "input",
            "message": "Enter 32nd notes to skip:",
            "name": "direct",
            "validator": OffsetValidator
        }]
        answers = prompt(questions)
        r = answers('direct')
        self.context.offset = r
        self.transition(States.SUCCESS)
        return False

    state_function = {
        "top": top,
        "nudging": nudging,
        "direct": direct,
        "preview": preview
    }

    def run(self):
        return NudgeMachine.state_function[self.state.value]()

    def transition(self, state):
        self.state = state


def choose_offset(media_info: MediaInfo):
    nc = NudgeMachineContext(media_info)
    n = NudgeMachine(nc)
    while n.run():
        pass
    if n.state == States.SUCCESS:
        return n.context.offset
    return None
