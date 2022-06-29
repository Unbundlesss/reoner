from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import BufferControl, HSplit, Window, Layout
from prompt_toolkit.layout.processors import Transformation, TransformationInput, Processor


# from reoner.cli.items import Option, Header, Blank

class MenuItem:
    focusable = False
    text_style = 'fg:white'
    focused_style = None
    highlighted_style = None
    indent = 0

    @classmethod
    def set_highlighted_style(cls, instyle):
        cls.highlighted_style = instyle

    @classmethod
    def set_style(cls, instyle):
        cls.style = instyle


class Focusable(MenuItem):
    focusable = True
    highlighted_style = 'fg:black bg:lightcyan'

    def am_selected(self):
        menu = Menu.get_instance()
        selected = menu.get_selection()
        return selected == self


class Option(Focusable):
    text_style = 'fg:white'
    focused_style = 'fg:lightcyan'
    highlighted_style = 'fg:black bg:lightcyan'
    indent = 2

    def __init__(self, order, focusable_order, text):
        self.text = text
        self.order = order
        self.focusable_order = focusable_order


class Blank(MenuItem):
    focusable = False

    def __init__(self, order):
        self.text = ''
        self.order = order


class Header(MenuItem):
    focusable = False
    text_style = 'fg:white'
    focused_style = None
    highlighted_style = None
    indent = 0

    def __init__(self, order, text):
        self.text = text
        self.order = order


class MenuColorizer(Processor):
    def apply_transformation(self, ti):
        menu = Menu.get_instance()
        return Menu.transform_line(menu, ti)


class Menu:
    instance = None

    @classmethod
    def set_singleton(cls, instance):
        cls.instance = instance

    @classmethod
    def get_instance(cls):
        return cls.instance

    def __init__(self,
                 options=None,
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

        # Put a reference to the instance in the class.
        # Lazy way of making the lines retrievable from anywhere
        Menu.set_singleton(self)

        if header:
            self.add_header(header)

        if options:
            for i in options:
                self.add_option(i)

        text = '\n'.join(map(lambda _x: _x.text, self.items))
        self.doc = Document(text, cursor_position=self.pos)
        self.buf = Buffer(read_only=True, document=self.doc)
        # self.buf_ctl = BufferControl(self.buf, input_processors=[MenuColorizer()])
        self.buf_ctl = BufferControl(self.buf,input_processors=[MenuColorizer()])
        self.split = HSplit([Window(self.buf_ctl, wrap_lines=False, always_hide_cursor=True)])

        # Scroll to initial spot
        for _ in range(self.initial_pos + 1):
            self.move_selection(1)

        self.app = Application(
            layout=Layout(self.split),
            full_screen=True,
            mouse_support=False,
            key_bindings=self.bind_keys())

    @staticmethod
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
        elif item.am_selected():
            prefix += '{}{}'.format(menu.cursor, menu.option_prefix)
            frag_list = [(item.highlighted_style, t) for s, t in ti.fragments]
        else:
            prefix += '{}{}'.format(' ' * len(menu.cursor), menu.option_prefix)
            frag_list = [(s if s else item.text_style, t) for s, t in ti.fragments]

        return Transformation([('', indent), ('', prefix)] + frag_list)



    def bind_keys(self):
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

        self.kb = kb
        return kb

    def add_option(self, text):
        self.total_lines += 1
        self.total_focusable_items += 1
        self.items.append(Option(
            order=self.total_lines - 1,
            focusable_order=self.total_focusable_items - 1,
            text=text
        ))

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

    def get_selection(self):
        for i in self.get_options():
            if i.focusable and i.focusable_order == self.pos:
                return i
        return None

    def move_selection(self, direction):
        # find the next focusable item in the specified direction
        if not any(item.focusable for item in self.items):
            raise RuntimeError("No focusable item found")

        self.pos = (self.pos + direction) % self.total_focusable_items
        focus = self.get_selection()
        self.buf.cursor_position = self.doc.translate_row_col_to_index(focus.order, 0)

    def run(self):
        self.app.run()
