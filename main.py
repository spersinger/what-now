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


        # 1. Read grayscale
        img = cv2.imread(file_name, cv2.IMREAD_GRAYSCALE)

        # 3. CLAHE for contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        img = clahe.apply(img)

        cv2.imwrite("ocr.png", img)

        # 5. OCR
        '''
        Page segmentation modes (--psm):
            0    Orientation and script detection (OSD) only.
            1    Automatic page segmentation with OSD.
            2    Automatic page segmentation, but no OSD, or OCR.
            3    Fully automatic page segmentation, but no OSD. (Default)
            4    Assume a single column of text of variable sizes.
            5    Assume a single uniform block of vertically aligned text.
            6    Assume a single uniform block of text.
            7    Treat the image as a single text line.
            8    Treat the image as a single word.
            9    Treat the image as a single word in a circle.
            10    Treat the image as a single character.
            11    Sparse text. Find as much text as possible in no particular order.
            12    Sparse text with OSD.
            13    Raw line. Treat the image as a single text line,
                    bypassing hacks that are Tesseract-specific.
                        '''
        text = pytesseract.image_to_string(
            "ocr.png",
            config="--oem 1 --psm 12 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789()[]/,-:."
        )
        print(text)

        print("Captured")
    def upload(self):
        '''
        Function to upload images from a camera roll or desktop
        '''
        chooser = FileChooserIconView(filters=['*.png', '*.jpg', '*.jpeg'])
        btn = Button(text="Select", size_hint_y=None, height=40)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(chooser)
        layout.add_widget(btn)

        popup = Popup(title="Select Image", content=layout,
                      size_hint=(0.9, 0.9))

        btn.bind(on_release=lambda *a: self.load_file(chooser, popup))
        popup.open()
 


class WhatNow(App):
    def build(self):
        self.title = "What Now?"
        return Root()

if __name__ == "__main__":
    WhatNow().run()

