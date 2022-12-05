import logging

from reoner.cli.interactive import generate_menu_layout
from reoner.cli.menu import Menu
from reoner.core.state import State


class FinishedState(State):
    def action(self):
        pass


class InitialState(State):
    def action(self):
        self.context.transition(BuildingMenu())


class BuildingMenu(State):
    def action(self):
        menu = Menu()
        menu.layout = generate_menu_layout(menu)
        menu.status_bar.set_text('Layout created')
        self.ui = menu
        self.context.transition(OpeningMenu())


class OpeningMenu(State):
    def action(self):
        menu = self.ui
        menu.status_bar.set_text('Initializing menu')
        menu.add_header(f"Reoner CLI")
        menu.add_options([('Pick file', 'p', 'Chooses an individual file to re-align.'),
                          ('Pick a folder', 'f', 'Chooses a folder to re-align.'),
                          ('Quit', 'q', 'Exit quietly.'),
                          ('Help', 'h', 'Get help.')
                          ])
        result = self.ui.run('Use arrow keys to make a choice. Press ctrl-c to quit.')
        v = result.value

        logging.debug(result.text)
        if v == 'q':
            self.context.transition(FinishedState('You quit good.'))
        elif v == 'f':
            menu.reset()
            menu.add_header("Finder thing")
            menu.add_blank()
            self.context.transition(OpeningMenu())
        elif v == 'a':
            menu.reset()
            menu.add_header("About thing")
            menu.add_blank()
            self.context.transition(OpeningMenu())
        elif v == 'p':
            menu.reset()
            menu.add_header("Pick thing thing")
            menu.add_blank()
            self.context.transition(OpeningMenu())

