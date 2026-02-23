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
from ui import *

Builder.load_file('../ui/themed.kv')
Builder.load_file('../ui/home_page.kv')
Builder.load_file('../ui/voice_page.kv')
Builder.load_file('../ui/scanner_page.kv')
Builder.load_file('../ui/whatnow.kv')


# custom classes from other source files
from document_scanner import DocumentScanner
import CalendarEvent
import Voice

class Home(Screen): pass
class Voice(Screen): pass

class Scanner(Screen):
    def on_enter(self):
        self.ids.cam_view.ids.camera.play = True

    def on_leave(self):
        self.ids.cam_view.ids.camera.play = False

class Edit(Screen): pass
class Root(BoxLayout):
    # TODO, fix this, it is janky but works.
    # The issue is that passing arguments from a .kv file is sorta hit or miss
    # so I hard code the screen_name onto the buttons, and then just 
    # don't use the screen name that is passed? I actually don't entirely know 
    # why this works, but it does so...
    def set_active(self, screen_name):
        sm = self.ids.sm
        # I guess this works here? Unsure why since printing screen name gives us
        # nothing, but it still switches the screen with sm (screen manager id)
        sm.current = screen_name

        for btn_id, name in (
            ("home_button", "Home"),
            ("voice_button", "Voice"),
            ("scanner_button", "Scanner"),
        ):
            btn = self.ids[btn_id]

            if btn.screen_name == screen_name:
                btn.text = f"[b]{name}[/b]"
                btn.color = (1, 1, 1, 1)  # selected color
            else:
                btn.text = name
                btn.color = (0.6, 0.6, 0.6, 1)  # unselected color

class WhatNow(App):
    def build(self):
        self.title = "What Now?"
        # string for voice input to be used by command interpreter
        self.voice_input = ""
        return Root()

if __name__ == "__main__":
    WhatNow().run()

