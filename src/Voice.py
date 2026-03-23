from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock

class Voice(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        try:
            import speech_recognition as sr
            self.r = sr.Recognizer()
            self.android = False
        except:
            print("on android; using plyer.stt")
            import plyer
            self.r = plyer.stt
            self.android = True
            if not plyer.stt.exist():
                self.r = None
                print("speech to text unavailable on this device")

    def record_button_pressed(self):
        
        text = self.ids.record_button.text
        
        if text == "Record":
            self.ids.record_button.text = "S1"
            self.ids.submit_voice_button.disabled = True
            
            if self.android:
                self.r.start()
            
        elif text == "Stop":
            self.ids.record_button.text = "R1"
            self.ids.submit_voice_button.disabled = False
            
            if self.android:
                self.r.stop()
                if len(self.r.results) != 0:
                    self.ids.voice_text_input.text = self.r.results[0]
            
            
        elif text == "S1":
            self.ids.record_button.text = "Stop"
        elif text == "R1":
            self.ids.record_button.text = "Record"

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
            mic_icon.source = "../mic_green.png"  # change to green
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
            mic_icon.source = "../mic_white.png"  # change back to white
            #enable submit button
            self.ids.submit_voice_button.disabled = False

            self.stop_event.set()

    def listen_loop(self):
        try:
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