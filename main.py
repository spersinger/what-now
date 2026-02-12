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
from kivy.uix.textinput import TextInput
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

# initialize the speech recognizer
r = sr.Recognizer()

class Home(Screen): pass


class Voice(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.listen_thread = None
        # used to stop recording
        self.stop_event = threading.Event()
        # used to change action of the record button
        # (start vs stop recording)
        self.listening = False

    def voice_to_string(self, text):
        app = App.get_running_app()
        app.voice_input += text + " "
        self.ids.voice_text_input.text += text + " "

        print(app.voice_input)
        return

    def start_voice(self):
        mic_icon = self.ids.mic_icon
        app = App.get_running_app()

        if not self.listening:
            #resets the input when recording is started
            app.voice_input = ""
            self.ids.voice_text_input.text = ""

            print("recording started")
            #disable submit button when recording
            self.ids.submit_voice_button.disabled = True
            # listening is started and event is not stopped
            self.listening = True
            self.stop_event.clear()

            # change button text when recording
            mic_icon.source = "mic_green.png"  # change to green
            self.ids.record_button.text = "Stop Recording"

            # thread for recording
            self.listen_thread = threading.Thread(
                target=self.listen_loop,
                daemon=True  # allows application to stop thread when closed
            )
            self.listen_thread.start()
        else:
            print("recording stopped")
            self.listening = False
            #disabled record button for 2 seconds
            self.ids.record_button.disabled = True
            Clock.schedule_once(lambda dt: setattr(self.ids.record_button, "disabled", False), 3)
            # change button text
            self.ids.record_button.text = "Record"
            mic_icon.source = "mic_white.png"  # change back to white
            #enable submit button
            self.ids.submit_voice_button.disabled = False

            self.stop_event.set()

    def listen_loop(self):
        try:
            with sr.Microphone() as source:
                # try to ignore background noise
                r.adjust_for_ambient_noise(source, duration=0.2)

                while not self.stop_event.is_set():
                    try:
                        # start recording, 5 seconds for a phrase
                        audio = r.listen(source, phrase_time_limit= 5)
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
        finally:
            self.listen_thread = None
            print("listen thread exited")

    # submit buttons function -- will eventually send text to command interpreter
    def submit_voice(self):
        if self.ids.voice_text_input.text is not "":
            print(self.ids.voice_text_input.text)
            app = App.get_running_app()
            app.voice_input = ""
            self.ids.voice_text_input.text = ""

    def on_leave(self):
        # If we are recording, stop
        if self.listening:
            print("Voice screen left – stopping recording")

            self.listening = False
            self.stop_event.set()

            # Reset voice screen
            if 'mic_icon' in self.ids:
                self.ids.mic_icon.source = "mic_white.png"
            if 'record_button' in self.ids:
                self.ids.record_button.text = "Record"
            if 'voice_text_input' in self.ids:
                self.ids.voice_text_input.text = ""
                app = App.get_running_app()
                app.voice_input = ""


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

