from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


class ReonerWindow(App):
    def build(self):
        self.window = GridLayout()
        # add widgets to window
        self.window.add_widget(Image(source="logo.png"))

        return self.window


if __name__ == "__main__":
    reoner = ReonerWindow()
    reoner.run()
