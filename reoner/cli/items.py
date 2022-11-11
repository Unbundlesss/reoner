class MenuItem:
    focusable = False
    text_style = 'fg:white'
    focused_style = None
    highlighted_style = None
    indent = 0

    @classmethod
    def set_highlighted_style(cls, in_style):
        cls.highlighted_style = in_style

    @classmethod
    def set_style(cls, in_style):
        cls.style = in_style


class Focusable(MenuItem):
    focusable = True
    highlighted_style = 'fg:black bg:lightcyan'


class Option(Focusable):
    text_style = 'fg:white'
    focused_style = 'fg:lightcyan'
    highlighted_style = 'fg:black bg:lightcyan'
    indent = 2

    def __init__(self, order, focusable_order, text: Optional[str] = None,
                 value: Optional[str] = None, status_line: Optional[str] = None):
        self.text = text
        self.value = value
        self.status_line = status_line
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
