from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
import speech_recognition as sr
import threading
from kivy.clock import Clock

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
        self.r = sr.Recognizer()


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
            if self.listen_thread and self.listen_thread.is_alive():
                self.listen_thread.join()

    def listen_loop(self):
        try:
            with sr.Microphone() as source:
                # try to ignore background noise
                self.r.adjust_for_ambient_noise(source, duration=0.2)

                while not self.stop_event.is_set():
                    try:
                        # start recording, 5 seconds for a phrase
                        audio = self.r.listen(source, timeout=1,phrase_time_limit= 7)
                        # using google for speech to text
                        text = self.r.recognize_google(audio)

                        # safely update app state from thread
                        Clock.schedule_once(
                            lambda dt, t=text: self.voice_to_string(t)
                        )
                    except sr.WaitTimeoutError:
                        pass
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
        text = self.ids.voice_text_input.text
        if text != "":

            app = App.get_running_app()

            #send text to command interpreter
            app.command_interpreter.generate_commands(text)

            #have schedule perform the commands
            #send each command to perform_commands
            #1 by 1
            cmd_list = app.command_interpreter.commands
            print("COMMANDS:", cmd_list)
            for c in cmd_list:
                print("RUNNING:", c.c_type, c.data)
                app.schedule.perform_command(c)

            # clear commands list after they are performed
            app.command_interpreter.commands = []

             #clear after sending
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
