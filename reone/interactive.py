import logging
import os
from typing import Union
from PyInquirer import prompt
from PyInquirer import style_from_dict
from pygments.token import Token
from pydub.playback import play
from pydub.exceptions import TooManyMissingFrames
from . import reone
from .pather import Pather


def _get_files(path):
    opts = os.listdir(path)
    opts = [{
                "name": f'{i}/',
                "value": i
            } if os.path.isdir(i) else i for i in opts if os.path.isdir(i) or i.endswith('.aiff')]
    opts.insert(0, "[quit]")
    opts.insert(0, "[up]")
    return opts


def _choose_file_prompt() -> Union[str, bool]:
    default_style = style_from_dict({
        Token.Separator: '#ansired',
        Token.QuestionMark: '#ansigreen',
        Token.Selected: '#ansiblue',
        Token.Pointer: '#ansiblue bold',
        Token.Instruction: '#ansiyellow',  # default
        Token.Answer: '#ansiyellow bold',
        Token.Question: '#ansiyellow',
    }, include_defaults=True)
    current_path = Pather(os.getcwd())
    print(current_path)
    questions = [
        {
            "type": "list",
            "name": "user_option",
            "message": "Choose file",
            "choices": _get_files(current_path),
        }
    ]
    answers = prompt(questions, style=default_style)
    user_option = answers.get("user_option")

    if user_option == "[quit]":
        return False
    elif user_option == "[up]":
        current_path.cd("../")
        return True
    elif os.path.isdir(user_option):
        current_path.cd(user_option)
        return True
    return user_option


def choose_file() -> Union[str, bool]:
    while loop := _choose_file_prompt():
        if type(loop) == bool and loop:
            continue
        else:
            break
    return loop


def choose_offset(file, bpm, f32details):
    logging.debug(f"total32nds: {f32details[1]}")
    result = nudge_loop(file, bpm, 0, f32details)
    while True:
        if result[0] == "keep-looping":
            result = nudge_loop(file, bpm, result[1], f32details)
        else:
            break

    if result[0] == "quit":
        return False
    elif result[0] == "start":
        return result[1]


def nudge_loop(file, bpm, offset, f32details):
    print(f"You are listening to:\n {file}")
    logging.debug(f32details)
    [f32nds, total32nds] = f32details

    questions = [{
        "type": "list",
        "name": "nudge_option",
        "message": f"Current offset is {offset}.",
        "choices": [ {
            "name": "Start it later.",
            "value": "make-bigger"
        }, {
            "name": "Start it earlier.",
            "value": "make-smaller"
        },{
            "name": f"Preview loop starting at {offset}",
            "value": "preview"
        }, {
            "name": "Start here.",
            "value": "start"
        },{
            "name": "Start it half bar later.",
            "value": "make-bigger-bigger"
        }, {
            "name": "Quit",
            "value": "quit"
        }],
    }]
    answers = prompt(questions)
    nudge_option = answers.get("nudge_option")
    if nudge_option == "make-bigger-bigger":
        offset = (total32nds, offset + 16)[offset < total32nds]
        return ["keep-looping", offset]
    if nudge_option == "make-bigger":
        offset = (total32nds, offset + 1)[offset < total32nds]
        return ["keep-looping", offset]
    elif nudge_option == "make-smaller":
        offset = (0, offset - 1)[offset >= 1]
        return ["keep-looping", offset]
    elif nudge_option == "preview":
        try:
            segment = reone(file, bpm, offset, f32details)
            preview = segment[0:2000]
            print('Playing.')
            play(preview)
        except TooManyMissingFrames:
            print('Segment is too short to preview')
        return ["keep-looping", offset]
    return [nudge_option, offset]
