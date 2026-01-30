from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
from kivy.core.window import Window
import speech_recognition as sr
import threading
from kivy.clock import Clock
import time

Window.size = (440,946)
Config.set('kivy', 'camera', 'opencv')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '440')
Config.set('graphics', 'height', '946')

class Home(Screen): pass


class Voice(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # used to stop recording
        self.stop_event = threading.Event()
        # used to change action of the record button
        # (start vs stop recording)
        self.listening = False

    def voice_to_string(self, text):
        app = App.get_running_app()
        app.voice_input += text + " "
        print(app.voice_input)
        return

    def start_voice(self):

        if not self.listening:
            print("recording started")
            # listening is started and event is not stopped
            self.listening = True
            self.stop_event.clear()

            # change button text when recording
            self.ids.record_button.text = "Stop Recording"

            # thread for recording
            threading.Thread(
                target=self.listen_loop,
                daemon=True  # allows application to stop thread when closed
            ).start()
        else:
            print("recording stopped")
            self.listening = False

            # change button text
            self.ids.record_button.text = "Record"

            self.stop_event.set()

    def listen_loop(self):
        with sr.Microphone() as source:
            while not self.stop_event.is_set():
                try:
                    # try to ignore background noise
                    r.adjust_for_ambient_noise(source, duration=0.2)
                    # start recording
                    audio = r.listen(source)
                    # using google for speech to text
                    text = r.recognize_google(audio)

                    # safely update app state from thread
                    Clock.schedule_once(
                        lambda dt, t=text: self.voice_to_string(t)
                    )

                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    Clock.schedule_once(
                        lambda dt: print("Speech service error")
                    )


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
        # string for voice input to be used by command interpreter
        self.voice_input = ""
        return Root()

if __name__ == "__main__":
    WhatNow().run()

