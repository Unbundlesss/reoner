import logging

from reoner.cli.menu import Menu
from reoner.core.state import State


class FinishedState(State):
    def action(self):
        pass


class InitialState(State):
    def action(self):
        self.context.transition(OpeningMenu())


class OpeningMenu(State):
    def action(self):
        header = f"Reoner CLI"
        options = [('Pick file', 'pick_file'),
                   ('Pick a folder', 'folder'),
                   ('Quit', 'quit'),
                   ('About', 'about')
                   ]

        menu = Menu(
            header=header,
            options=options
        )

        result = menu.run()
        logging.debug(result.text)
        if result.value == 'quit':
            self.context.transition(FinishedState())

    # Attach accept handler to the input field. We do this by assigning the
    # handler to the `TextArea` that we created earlier. it is also possible to
    # pass it to the constructor of `TextArea`.
    # NOTE: It's better to assign an `accept_handler`, rather than adding a
    #       custom ENTER key binding. This will automatically reset the input
    #       field and add the strings to the history.
    # def accept(buff):
    #     # Evaluate "calculator" expression.
    #     try:
    #         output = "\n\nIn:  {}\nOut: {}".format(
    #             input_field.text, eval(input_field.text)
    #         )  # Don't do 'eval' in real code!
    #     except BaseException as e:
    #         output = f"\n\n{e}"
    #     new_text = output_field.text + output
    #
    #     # Add text to output buffer.
    #     output_field.buffer.document = Document(
    #         text=new_text, cursor_position=len(new_text)
    #     )
    #
    # input_field.accept_handler = accept
