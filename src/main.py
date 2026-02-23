from kivy.config import Config
import os
import sys
Config.set('kivy', 'camera', 'opencv')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('kivy', 'keyboard_mode', 'system')

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
from kivy.clock import Clock

from kivy.core.window import Window
from kivy.lang import Builder


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
class Root(BoxLayout): pass

class WhatNow(App):
    kv_file = None
    
    def build(self):
        self.title = "What Now?"
        self.voice_input = ""
        
        # Get the correct path for both development and PyInstaller
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            base_path = sys._MEIPASS
        else:
            # Running in normal Python
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        kv_path = os.path.join(base_path, 'main.kv')
        print(kv_path)
        Builder.load_file(kv_path)
        
        Clock.schedule_once(self.init_camera, 0.5)
        return Root()

    
    def init_camera(self, dt):
        try:
            scanner_screen = self.root.ids.sm.get_screen('scanner')
            camera = scanner_screen.ids.cam_view.ids.camera
            camera.index = 0
            camera.play = False
        except Exception as e:
            print(f"Could not start camera: {e}")
            # Handle gracefully - maybe show a label instead



if __name__ == "__main__":
    WhatNow().run()

