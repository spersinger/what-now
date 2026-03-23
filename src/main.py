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

<DocumentScanner>:
    orientation: 'vertical'

    BoxLayout:
        id: camera_container
   # Camera:
    #    id: camera
     #   resolution: (640, 480)
      #  play: False

    Label:
        id: loading_text
        opacity: 0
        text: "Loading..."

    BoxLayout:
        size_hint_y: None
        height: '48dp'
        anchor_x: 'center'
        anchor_y: 'center'

        Button:
            id: scan_button
            text: 'Scan'
            size_hint_x: 0.25
            size_hint_y: None
            height: '48dp'
            on_press: root.capture()
            disabled: False

        Button:
            id: upload_button
            text: 'Upload'
            size_hint_x: 0.25
            size_hint_y: None
            height: '48dp'
            on_press: root.upload()
            disabled: True


<Home>:
    Label:
        text: "Home Screen"

<Voice>:
    BoxLayout:
        orientation: "vertical"
        padding: 10
        spacing: 10

        id: voice_root

        canvas.before:
            Color:
                rgba: 0.10, 0.20, 0.45, 1  # Blue background
            Rectangle:
                pos: self.pos
                size: self.size


        # Mic icon and text label in the center
        AnchorLayout:
            anchor_x: "center"
            anchor_y: "center"

            BoxLayout:
                orientation: "vertical"
                spacing: 20
                size_hint_x: 0.95
                size_hint_y: None
                size: self.minimum_size

                TextInput:
                    id: voice_text_input  #will be used to show voice input to user

                    hint_text: "Record to start!"
                    font_size: "16sp"
                    size_hint_x: 1

                    size_hint_y: None
                    height: "50dp"

                Image:
                    id: mic_icon
                    source: "../mic_white.png"
                    size_hint: None, None
                    size: "96dp", "96dp"
                    pos_hint: {"center_x": 0.5}


        Button:
            id: record_button
            text: "Record"
            size_hint_y: None
            height: "48dp"

            background_normal: ""
            background_down: ""
            background_color:
                (0.26, 0.38, 0.54, 1) if self.state == 'down' else (0.32, 0.45, 0.62, 1)

            on_release: root.record_button_pressed()
        Button:
            id: submit_voice_button
            text: "Submit"
            disabled: True
            size_hint_y: None
            height: "48dp"

            background_normal: ""
            background_down: ""
            background_color:
                (0.26, 0.38, 0.54, 1) if self.state == 'down' else (0.32, 0.45, 0.62, 1)

            on_release: root.submit_voice()




<Scanner>:
    DocumentScanner:
        id: cam_view
        padding: [0, 0, 0, 20]  # left, top, right, bottom: 20px gap

<Edit>:
    Label:
        text: "Edit Screen"                 
''')


# custom classes from other source files
from Voice import Voice
from DocumentScanner import DocumentScanner

class Home(Screen): pass

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
        
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.CAMERA,
                Permission.RECORD_AUDIO,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
            ])
        except:
            print("not on android; continuing")
        
        self.title = "What Now?"
        # string for voice input to be used by command interpreter
        self.voice_input = ""
        return Root()

if __name__ == "__main__":
    WhatNow().run()
