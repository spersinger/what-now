from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder

Builder.load_string('''
<Home>:
    Label:
        text: "Home Screen"
''')

class Home(Screen): pass