from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.config import Config
from kivy.core.window import Window

import time
import pytesseract
import numpy as np
import cv2
from PIL import Image

Window.size = (440,946)
Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('input', 'mtdev_%(name)s', '')
Config.set('input', 'hid_%(name)s', '')
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
        '''
        Function to capture the images and give them the names
        according to their captured time and date.
        '''
        camera = self.ids['camera']
        timestr = time.strftime("%Y%m%d_%H%M%S")
        file_name = "IMG_{}.png".format(timestr)
        camera.export_to_png(file_name)

        print("Captured")
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

