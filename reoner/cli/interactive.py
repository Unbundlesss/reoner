import logging
import os
import sys
from typing import Union

from PyInquirer import prompt
from PyInquirer import style_from_dict
from pygments.token import Token

from ..core.utils import get_files
from ..core.reoneablemedia import ReoneableMedia
from ..core.pather import Pather

__all__ = ['choose_offset', 'choose_file']

autoplay = True


def _get_files(path):
    opts = get_files(path)
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


def choose_offset(seg: ReoneableMedia):
    global autoplay
    logging.debug(f"total32nds: {seg.total32nds}")
    result, status = nudge_loop(seg)
    while result is True:
        result, status = nudge_loop(seg)
        logging.debug(f"status: {status}")

    if status == "quit":
        sys.exit(0)
    elif status == "error":
        sys.exit(1)
    elif status == "start":
        return seg


def nudge_loop(media: ReoneableMedia):
    global autoplay
    print(f"You are listening to:\n {media.filename}")
    automessage = {
        "name": "Turn off autoplay",
        "value": "auto-off"} if autoplay else {
        "name": "Turn on autoplay",
        "value": "auto-on"
    }

    questions = [{
        "type": "list",
        "name": "nudge_option",
        "message": f"Current offset is {media.offset}.",
        "choices": [{
            "name": "Start it later.",
            "value": "make-bigger"
        }, {
            "name": "Start it earlier.",
            "value": "make-smaller"
        }, {
            "name": f"Preview loop starting at {media.offset}",
            "value": "preview"
        }, {
            "name": "Stop playback.",
            "value": "stop"
        }, {
            "name": "Start here.",
            "value": "start"
        }, {
            "name": "Start it half bar later.",
            "value": "make-bigger-bigger"
        }, automessage, {
            "name": "Quit",
            "value": "quit"
        }],
    }]
    answers = prompt(questions)
    nudge_option = answers.get("nudge_option")
    if nudge_option == "make-bigger-bigger":
        media.offset += 16
        if autoplay:
            media.play()
        return True, None
    if nudge_option == "make-bigger":
        media.offset += 1
        if autoplay:
            media.play()
        return True, None
    elif nudge_option == "make-smaller":
        media.offset -= 1
        if autoplay:
            media.play()
        return True, None
    elif nudge_option == "preview":
        media.play()
        return True, None
    elif nudge_option == "stop":
        media.stop()
        return True, None
    elif nudge_option == "auto-on":
        autoplay = True
        media.play()
        return True, None
    elif nudge_option == "auto-off":
        autoplay = False
        return True, None
    elif nudge_option == "start":
        return False, 'start'

    print("Something went wrong")
    return False, "error"
