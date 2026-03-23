from Cython import Build
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
import threading
from kivy.clock import Clock
from kivy.utils import platform
from kivy.lang import Builder

Builder.load_string('''
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
                    source: "mic_white.png"
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

            on_release: root.start_voice()
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
''')

# testing
try:
    import speech_recognition as sr
except:
    print("speechrecognition import failed.")
if platform == 'android':
    from plyer import stt
else:
    import speech_recognition as sr

class Voice(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.listen_thread = None
        
        # used to stop recording
        self.stop_event = threading.Event()
        
        # used to change action of the record button
        # (start vs stop recording)
        self.listening = False
        
        # initialize the speech recognizer
        try: # will fail if on android
            self.r = sr.Recognizer()
        except:
            print("running on android.")


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
            if platform == 'android':
                if stt.exist():
                    stt.start()
            else:
                self.listen_thread = threading.Thread(
                    target=self.listen_loop,
                    daemon=True  # allows application to stop thread when closed
                )
                self.listen_thread.start()
        else:
            print("recording stopped")
            self.listening = False
            if platform == 'android' and stt.listening:
                stt.stop()
            
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
            if platform != 'android':
                with sr.Microphone() as source:
                    # try to ignore background noise
                    self.r.adjust_for_ambient_noise(source, duration=0.2)

                    while not self.stop_event.is_set():
                        try:
                            # start recording, 5 seconds for a phrase
                            audio = self.r.listen(source, phrase_time_limit= 5)
                            # using google for speech to text
                            text = self.r.recognize_google(audio)

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
        if self.ids.voice_text_input.text != "":
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
