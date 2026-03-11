from kivy.config import Config
Config.set('kivy', 'camera', 'opencv')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('kivy', 'keyboard_mode', 'system')
# For fixing multitouch
Config.remove_option('input', '%(name)s')
Config.set('input', 'mouse', 'mouse')

try:
    from kivy.app import App
except ModuleNotFoundError:
    print("\nKivy was not found. Possible issues:")
    print("\t- python3.13 not used. check with `python --verison` and run `source setup.sh`")
    print("\t- kivy was never installed. run `source setup.sh` to check, install, or view install errors.")
    quit()
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

from kivy.core.window import Window
from kivy.lang import Builder

Builder.load_file('../whatnow.kv')


# custom classes from other source files
from document_scanner import DocumentScanner
import CalendarEvent
import Voice

class Home(Screen): pass
class Voice(Screen): pass

class Scanner(Screen):
    def on_enter(self):
        if hasattr(self.ids.cam_view, "camera"):
            self.ids.cam_view.camera.play = True

    def on_leave(self):
        if hasattr(self.ids.cam_view, "camera"):
            self.ids.cam_view.camera.play = False

class Edit(Screen): pass
class Root(BoxLayout): pass


class WhatNow(App):
    def build(self):
        self.title = "What Now?"
        # string for voice input to be used by command interpreter
        self.voice_input = ""
        return Root()

if __name__ == "__main__":
    WhatNow().run()

