from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import BufferControl, HSplit, Window, Layout, FormattedTextControl, WindowAlign
from prompt_toolkit.layout.processors import Transformation, TransformationInput, Processor
from typing import Optional, List, Tuple, Union
from prompt_toolkit.key_binding import merge_key_bindings
from .items import Option, Blank, Header

OptionTuple = Tuple[str, Optional[str], Optional[str]]
OptionTupleList = list[OptionTuple]
MaybeOption = Optional[Option]


class StatusBar:
    def __init__(self):
        self._text = ""

    def get_status_bar_text(self):
        return self._text

    def set_text(self, text):
        self._text = text


class MenuColorizer(Processor):
    def apply_transformation(self, ti):
        menu = Menu.get_instance()
        return transform_line(menu, ti)


def transform_line(menu, ti: TransformationInput) -> Transformation:
    if len(list(ti.fragments)) == 0:
        return Transformation(ti.fragments)

    # ti comes with line number. Use this to lookup full item
    item = menu.items[ti.lineno]

    # cursor
    prefix = ''
    indent = (item.indent + menu.left_margin) * ' '

    # if this line has a text_style, apply it.
    if not item.focusable:
        frag_list = [(s if s else item.text_style, t) for s, t in ti.fragments]
    elif item == menu.get_selection():
        prefix += '{}{}'.format(menu.cursor, menu.option_prefix)
        frag_list = [(item.highlighted_style, t) for s, t in ti.fragments]
    else:
        prefix += '{}{}'.format(' ' * len(menu.cursor), menu.option_prefix)
        frag_list = [(s if s else item.text_style, t) for s, t in ti.fragments]

    return Transformation([('', indent), ('', prefix)] + frag_list)


class Menu:
    instance = None

    @classmethod
    def set_singleton(cls, instance):
        cls.instance = instance

    @classmethod
    def get_instance(cls):
        return cls.instance

    def add_key_bindings(self, key_bindings: KeyBindings):

        if not isinstance(self.kb, KeyBindings):
            raise Exception('default keybindings are not set.')

        bindings = merge_key_bindings([self.kb, key_bindings])
        self.kb = bindings

    def __init__(self,
                 options: Union[OptionTupleList, None] = None,
                 header=None,
                 initial_pos=0,
                 left_margin=2):
        self.pos = 0  # only considers the focusable elements
        self.initial_pos = initial_pos  # for resuming selection
        self.items = []  # list of all items
        self.cursor = '▶'
        self.total_lines = 0  # essentially should be length of items[]
        self.total_focusable_items = 0  # focusable items
        self.option_prefix = ' '
        self.left_margin = left_margin
        self.kb = None
        self.app = None
        self.split = None
        self._layout = None
        self.status_bar = StatusBar()
        self.status_bar.set_text("Use arrow keys and select option.")

        if header:
            self.add_header(header)

        if options:
            for i in options:
                self.add_option(i)

        self.doc = Document(self.get_text(), cursor_position=self.pos)
        self.buf = Buffer(read_only=False, document=self.doc)
        self.buf_ctl = BufferControl(buffer=self.buf, input_processors=[MenuColorizer()])
        self.prep_default_key_bindings()
        # Put a reference to the instance in the class.
        # Lazy way of making the lines retrievable from anywhere
        Menu.set_singleton(self)

    @property
    def layout(self):
        return self._layout

    @layout.setter
    def layout(self, value: Layout):
        self._layout = value

    def get_text(self):
        return '\n'.join(map(lambda _x: _x.text, self.items))

    def jump_selection(self, position):
        # reset position
        self.pos = 0
        # reset cursor
        focus = self.get_selection()
        self.buf.cursor_position = self.doc.translate_row_col_to_index(focus.order, 0)
        # bang through the selections
        for x in range(0, position):
            self.move_selection(1)

    def prep_default_key_bindings(self):
        kb = KeyBindings()

        @kb.add('c-c')
        def _(e):
            e.app.exit()

        @kb.add('up')
        def _(e):
            self.move_selection(-1)

        @kb.add('down')
        def _(e):
            self.move_selection(1)

        @kb.add('enter')
        def _(e):
            self.app.exit(self.get_selection())

        self.kb = kb
        return kb

    def add_option(self, option: OptionTuple):
        self.total_lines += 1
        self.total_focusable_items += 1
        self.items.append(
            Option(self.total_lines - 1, self.total_focusable_items - 1, *option))

    def add_options(self, options: OptionTupleList):
        for i in options:
            self.add_option(i)

    def reset(self):
        self.total_lines = 0
        self.initial_pos = 0
        self.pos = 0
        self.total_focusable_items = 0
        self.items = []

    def add_blank(self):
        self.total_lines += 1
        self.items.append(Blank(self.total_lines - 1))

    def add_header(self, title):
        for text in title.split('\n'):
            self.total_lines += 1
            self.items.append(Header(
                order=self.total_lines - 1,
                text=text
            ))

    def get_options(self):
        return [i for i in self.items if isinstance(i, Option)]

    def get_selection(self) -> MaybeOption:
        opts = self.get_options()
        for i in opts:
            if i.focusable and i.focusable_order == self.pos:
                return i
        return None

    def move_selection(self, direction):
        # find the next focusable item in the specified direction
        if not any(item.focusable for item in self.items):
            raise RuntimeError("No focusable item found")

        self.pos = (self.pos + direction) % self.total_focusable_items
        focus = self.get_selection()
        if focus.status_line is not None:
            self.status_bar.set_text(focus.status_line)
        self.buf.cursor_position = self.doc.translate_row_col_to_index(focus.order, 0)

    def run(self, status='ready') -> MaybeOption:
        app = Application(
            layout=self.layout,
            full_screen=True,
            mouse_support=False,
            key_bindings=self.kb)

        self.app = app
        self.buf.text = self.get_text()

        # Scroll to initial spot
        self.jump_selection(self.initial_pos)

        if not isinstance(self.kb, KeyBindings):
            raise Exception('KeyBindings not properly configured.')

        if self.total_focusable_items < 1:
            raise Exception('There are no selectable options provided.')

        self.status_bar.set_text(status)

        return self.app.run()
