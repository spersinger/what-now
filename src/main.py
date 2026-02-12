try:
    from kivy.app import App
except ModuleNotFoundError:
    print("\nKivy was not found. Possible issues:")
    print("\t- python3.13 not used. check with `python --verison` and run `source setup.sh`")
    print("\t- kivy was never installed. run `source setup.sh` to check, install, or view install errors.")
    quit()
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
from kivy.core.window import Window
from kivy.lang import Builder

Builder.load_file('../whatnow.kv')

# custom classes from other source files
from CalendarEvent import CalendarEvent

Window.size = (440,946)
Config.set('kivy', 'camera', 'opencv')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '440')
Config.set('graphics', 'height', '946')

class Home(Screen): pass
class Voice(Screen): pass
class Scanner(Screen):
    def on_enter(self):
        self.ids.cam_view.ids.camera.play = True

    def on_leave(self):
        self.ids.cam_view.ids.camera.play = False

class Edit(Screen): pass

class Root(BoxLayout):
    pass


class CameraClick(BoxLayout):
    def capture(self):
        print("Captured todo")
    def upload(self):
        '''
        Function to upload images from a camera roll or desktop
        '''
        print("Upload todo")


class WhatNow(App):
    def build(self):
        self.title = "What Now?"
        return Root()

if __name__ == "__main__":
    WhatNow().run()

