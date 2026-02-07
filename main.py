import os
os.environ["KIVY_NO_MTDEV"] = "1"
os.environ["KIVY_NO_EVDEV"] = "1"

# Disable Linux multi-touch devices
from kivy.config import Config
Config.set('input', 'mtdev_%(name)s', 'ignore')
Config.set('input', 'hid_%(name)s', 'ignore')
Config.set("input", "mouse", "mouse,disable_multitouch")

# Optional: disable mouse emulation from touch
Config.set('input', 'mouse', 'mouse,disable_multitouch')

Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('input', 'mtdev_%(name)s', '')
Config.set('input', 'hid_%(name)s', '')
Config.set('kivy', 'camera', 'opencv')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '440')
Config.set('graphics', 'height', '946')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

from image_scanner import *
from document_scanner import DocumentScanner

Window.size = (440,946)

parser = LocalSyllabusParser()

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


class WhatNow(App):
    def build(self):
        self.title = "What Now?"
        return Root()

if __name__ == "__main__":
    WhatNow().run()
