from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
from kivy.core.window import Window

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

