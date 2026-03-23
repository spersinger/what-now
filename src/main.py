try:
    from kivy.app import App
except ModuleNotFoundError:
    print("\nKivy was not found. Possible issues:")
    print("\t- python3.13 not used. check with `python --verison` and run `source setup.sh`")
    print("\t- kivy was never installed. run `source setup.sh` to check, install, or view install errors.")
    quit()
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.config import Config
from kivy.utils import platform

if platform == 'android':
    from android.permissions import Permission, request_permissions
    request_permissions([
        Permission.CAMERA,
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.READ_EXTERNAL_STORAGE,
        Permission.RECORD_AUDIO
    ])
    

Builder.load_string('''
<Root>:
    orientation: "vertical"
    BoxLayout:
        size_hint_y: None
        height: 60
        spacing: 10

    ScreenManager:
        id: sm

        Home:
            name: "home"
        Voice:
            name: "voice"
        Scanner:
            name: "scanner"

    BoxLayout:
        size_hint_y: None
        height: 60
        spacing: 10
        padding:5

        canvas.before:
            Color:
                rgba: 0.32, 0.45, 0.62, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Button:
            text: "Home"

            background_normal: ""
            background_down: ""
            background_color:
                (0.78, 0.36, 0.14, 1) if self.state == 'down' else (0.06, 0.12, 0.30, 1)

            on_release: sm.current = "home"
        Button:
            text: "Voice"

            background_normal: ""
            background_down: ""
            background_color:
                (0.78, 0.36, 0.14, 1) if self.state == 'down' else (0.06, 0.12, 0.30, 1)

            on_release: sm.current = "voice"
        Button:
            text: "Scanner"

            background_normal: ""
            background_down: ""
            background_color:
                (0.78, 0.36, 0.14, 1) if self.state == 'down' else (0.06, 0.12, 0.30, 1)

            on_release: sm.current = "scanner"
''')

Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('kivy', 'keyboard_mode', 'system')

# For fixing multitouch
Config.remove_option('input', '%(name)s')
Config.set('input', 'mouse', 'mouse')

# import used classes
from DocumentScanner import DocumentScanner
from Home import Home
from Voice import Voice

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