import os
from typing import Union

from PyInquirer import prompt

from .interactive import default_style
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
    start_path = Pather(os.getcwd())
    try:
        while loop := _choose_file_prompt():
            if type(loop) == bool and loop:
                continue
            else:
                break
        return loop
    except Exception:
        Pather(start_path).cd()