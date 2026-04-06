from kivy.app import App

from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
import speech_recognition as sr
import threading
from kivy.clock import Clock
import re


from Command import CommandType
from globals import user_schedule, command_interpreter
import CalendarEvent


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

        #print(app.voice_input)
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

    # submit buttons function - send text to command interpreter and perform commands
    def submit_voice(self):
        text = self.ids.voice_text_input.text
        if text != "":

            app = App.get_running_app()

            parts = text.split(" and ")

            for part in parts:
                #send text to command interpreter
                command_interpreter.generate_commands(part)

            #have schedule perform the commands
            #send each command to perform_commands
            #1 by 1
            cmd_list = command_interpreter.commands
            self.commands_to_process = cmd_list
            self.current_command_index=0
            self.show_next_command()


            # clear commands list after they are performed
            command_interpreter.commands = []

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


    def build_accept_command_ui_popup(self, command):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint = (1,1))
        button_box = BoxLayout(orientation='horizontal', padding=10, spacing=10, height = 50)
        #inputs for changed TextInput to be placed in data
        inputs = {}

        if command.c_type == CommandType.ADD:

            command_label = Label(text='Command:', size_hint_y=None, height=30, halign='left')
            command_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
            command_input = TextInput(
                text=str(command.c_type.name),
                multiline=True,
                size_hint_x=1,
                size_hint_y=None,
                height=35
            )
            inputs["type"] = command_input

            name_label = Label(text='Name:', size_hint_y=None, height=30, halign='left')
            name_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
            name_text_input = TextInput(
                text=str(command.data.name),
                multiline=True,
                size_hint_x=1,
                size_hint_y=None,
                height=35
            )
            inputs["name"] = name_text_input

            desc_label = Label(text='Desc:', size_hint_y=None, height=30, halign='left')
            desc_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
            desc_input = TextInput(
                text=str(command.data.description),
                multiline=True,
                size_hint_x=1,
                size_hint_y=None,
                height=35
            )
            inputs["desc"] = desc_input

            if command.data.notif_times:
                notifs = ", ".join(str(n) for n in command.data.notif_times)
            else:
                notifs = ""
            notif_label = Label(text='notifications:', size_hint_y=None, height=30, halign='left')
            notif_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
            notif_input = TextInput(
                text=notifs,
                multiline=True,
                size_hint_x=1,
                size_hint_y=None,
                height=35
            )
            inputs["notif"] = notif_input

            date_label = Label(text='Date range:', size_hint_y=None, height=30, halign='left')
            date_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
            date_input = TextInput(
                text=str(command.data.date_range),
                multiline=True,
                size_hint_x=1,
                size_hint_y=None,
                height=35
            )
            inputs["date"] = date_input

            time_label = Label(text='Time:', size_hint_y=None, height=30, halign='left')
            time_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
            time_input = TextInput(
                text=str(command.data.time_range),
                multiline=True,
                size_hint_x=1,
                size_hint_y=None,
                height=35
            )
            inputs["time"] = time_input

            repeat_label = Label(text='Repeat:', size_hint_y=None, height=30, halign='left')
            repeat_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
            repeat_input = TextInput(
                text=str(command.data.repeat),
                multiline=True,
                size_hint_x=1,
                size_hint_y=None,
                height=35
            )
            inputs["repeat"] = repeat_input

            content.add_widget(command_label)
            content.add_widget(command_input)

            content.add_widget(name_label)
            content.add_widget(name_text_input)

            content.add_widget(desc_label)
            content.add_widget(desc_input)

            content.add_widget(notif_label)
            content.add_widget(notif_input)

            content.add_widget(date_label)
            content.add_widget(date_input)

            content.add_widget(time_label)
            content.add_widget(time_input)

            content.add_widget(repeat_label)
            content.add_widget(repeat_input)

        elif command.c_type == CommandType.DELETE :
            command_label = Label(text='Command:', size_hint_y=None, height=30, halign='left')
            command_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
            command_input = TextInput(
                text=str(command.c_type.name),
                multiline=True,
                size_hint_x=1,
                size_hint_y=None,
                height=35
            )
            inputs["type"] = command_input

            name_label = Label(text='Name:', size_hint_y=None, height=30, halign='left')
            name_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
            name_text_input = TextInput(
                text=str(command.data.name),
                multiline=True,
                size_hint_x=1,
                size_hint_y=None,
                height=35
            )
            inputs["name"] = name_text_input

            # add command and name labels and input
            content.add_widget(command_label)
            content.add_widget(command_input)

            content.add_widget(name_label)
            content.add_widget(name_text_input)

            if command.data.date_range:
                date_label = Label(text='Date range:', size_hint_y=None, height=30, halign='left')
                date_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
                date_input = TextInput(
                    text=str(command.data.date_range),
                    multiline=True,
                    size_hint_x=1,
                    size_hint_y=None,
                    height=35
                )
                content.add_widget(date_label)
                content.add_widget(date_input)
                inputs["date"] = date_input


        elif command.c_type == CommandType.EDIT:

            old_event, new_event = command.data

            command_label = Label(text='Command:', size_hint_y=None, height=30, halign='left')
            command_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
            command_input = TextInput(
                text=str(command.c_type.name),
                multiline=True,
                size_hint_x=1,
                size_hint_y=None,
                height=35
            )
            inputs["type"] = command_input

            name_label = Label(text='Name:', size_hint_y=None, height=30, halign='left')
            name_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
            name_text_input = TextInput(
                text=str(new_event.name),
                multiline=True,
                size_hint_x=1,
                size_hint_y=None,
                height=35
            )
            inputs["name"] = name_text_input

            #add command and name labels and input
            content.add_widget(command_label)
            content.add_widget(command_input)

            content.add_widget(name_label)
            content.add_widget(name_text_input)

            # ONLY SHOW THE REST IF THEY ARE CHANGED
            if new_event.description:
                desc_label = Label(text='New Desc:', size_hint_y=None, height=30, halign='left')
                desc_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
                desc_input = TextInput(
                    text=str(new_event.description),
                    multiline=True,
                    size_hint_x=1,
                    size_hint_y=None,
                    height=35
                )
                content.add_widget(desc_label)
                content.add_widget(desc_input)
                inputs["desc"] = desc_input


            if new_event.notif_times:

                notif_label = Label(text='New notifications:', size_hint_y=None, height=30, halign='left')
                notif_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
                notif_input = TextInput(
                    text=str(new_event.notif_times),
                    multiline=True,
                    size_hint_x=1,
                    size_hint_y=None,
                    height=35
                )

                content.add_widget(notif_label)
                content.add_widget(notif_input)
                inputs["notif"] = notif_input


            if new_event.date_range:

                date_label = Label(text='New Date range:', size_hint_y=None, height=30, halign='left')
                date_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
                date_input = TextInput(
                    text=str(new_event.date_range),
                    multiline=True,
                    size_hint_x=1,
                    size_hint_y=None,
                    height=35
                )
                content.add_widget(date_label)
                content.add_widget(date_input)
                inputs["date"] = date_input


            if new_event.time_range:

                time_label = Label(text='New Time:', size_hint_y=None, height=30, halign='left')
                time_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
                time_input = TextInput(
                    text=str(new_event.time_range),
                    multiline=True,
                    size_hint_x=1,
                    size_hint_y=None,
                    height=35
                )
                content.add_widget(time_label)
                content.add_widget(time_input)
                inputs["time"] = time_input

            if new_event.repeat:

                repeat_label = Label(text='New Repeat:', size_hint_y=None, height=30, halign='left')
                repeat_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
                repeat_input = TextInput(
                    text=str(new_event.repeat),
                    multiline=True,
                    size_hint_x=1,
                    size_hint_y=None,
                    height=35
                )

                content.add_widget(repeat_label)
                content.add_widget(repeat_input)
                inputs["repeat"] = repeat_input

        accept_btn = Button(text='Accept', size_hint_x = 1)
        accept_btn.bind(on_press=lambda x: self.on_accept_command(command, inputs))

        reject_btn = Button(text='Reject', size_hint_x = 1)
        reject_btn.bind(on_press=lambda x: self.on_reject_command())

        button_box.add_widget(accept_btn)
        button_box.add_widget(reject_btn)

        content.add_widget(button_box)

        self.accept_command_popup = Popup(
            title='Verify Voice Command',
            content=content,
            size_hint=(0.8, 0.9),
            auto_dismiss=False
        )

    def show_next_command(self):
        if self.current_command_index < len(self.commands_to_process):
            command = self.commands_to_process[self.current_command_index]
            self.build_accept_command_ui_popup(command)
            self.accept_command_popup.open()

        else:
            # All commands processed
            # clear commands list after they are performed
            #app.command_interpreter.commands = []
            command_interpreter.commands = []
            Clock.schedule_once(self._cleanup)

    def on_accept_command(self,command, inputs):
        self.accept_command_popup.dismiss()

        #convert string to CommandType
        if "type" in inputs:
            text = inputs["type"].text.strip().upper()
            command.c_type = CommandType[text]

        if "name" in inputs:
            command.data.name = inputs["name"].text

        if "desc" in inputs:
            command.data.description = inputs["desc"].text

        if "notif" in inputs:
            text = inputs["notif"].text
            #split the string into a list
            notif_list = [n.strip() for n in text.split(",") if n.strip()]
            # parse notification list
            command.data.notif_times = command_interpreter.parse_notifications(notif_list)

        if "date" in inputs:
            text = inputs["date"].text
            if "->" in text:
                start_str, end_str = text.split("->")
                start_str = start_str.strip()
                end_str = end_str.strip()
            else:
                # single date
                start_str = end_str = text.strip()

            # create date range and put it in data
            start_date = command_interpreter.parse_date(start_str, command.c_type)
            end_date = command_interpreter.parse_date(end_str, command.c_type)
            command.data.date_range = CalendarEvent.DateRange(start_date,end_date)


        if "time" in inputs:
            text = inputs["time"].text
            parts = [p.strip() for p in re.split(r'\s*->\s*', text)]

            if len(parts) == 2:
                start_t, end_t = parts
            else:
                start_t = parts[0]
                end_t = None

            # create time range and put it in data
            command.data.time_range = command_interpreter.parse_time(start_t,end_t)

        if "repeat" in inputs:
            text = inputs["repeat"].text

            repeat_dict = self.text_to_repeat_dict(text)

            command.data.repeat = command_interpreter.parse_repeat(repeat_dict,command.data.date_range.start_date,command.data.date_range.end_date)

        user_schedule.perform_command(command)

        self.current_command_index += 1
        self.show_next_command()  # Show the next command

    def on_reject_command(self):
        self.accept_command_popup.dismiss()

        # just skip this command
        self.current_command_index += 1

        self.show_next_command()

    '''  DONT THINK WE SHOULD USE THIS
    def on_accept_all_commands(self, command,inputs):
        self.accept_command_popup.dismiss()

        # put new input into only the first command to be performed
        # convert string to CommandType
        if "type" in inputs:
            text = inputs["type"].text.strip().upper()
            command.c_type = CommandType[text]

        if "name" in inputs:
            command.data.name = inputs["name"].text

        if "desc" in inputs:
            command.data.description = inputs["desc"].text

        if "notif" in inputs:
            text = inputs["notif"].text
            # split the string into a list
            notif_list = [n.strip() for n in text.split(",") if n.strip()]
            # parse notification list
            command.data.notif_times = command_interpreter.parse_notifications(notif_list)

        if "date" in inputs:
            text = inputs["date"].text
            if "->" in text:
                start_str, end_str = text.split("->")
                start_str = start_str.strip()
                end_str = end_str.strip()
            else:
                # single date
                start_str = end_str = text.strip()

            # create date range and put it in data
            start_date = command_interpreter.parse_date(start_str, command.c_type)
            end_date = command_interpreter.parse_date(end_str, command.c_type)
            command.data.date_range = CalendarEvent.DateRange(start_date, end_date)

        if "time" in inputs:
            text = inputs["time"].text
            parts = [p.strip() for p in re.split(r'\s*->\s*', text)]

            if len(parts) == 2:
                start_t, end_t = parts
            else:
                start_t = parts[0]
                end_t = None

            # create time range and put it in data
            command.data.time_range = command_interpreter.parse_time(start_t, end_t)

        if "repeat" in inputs:
            text = inputs["repeat"].text

            repeat_dict = self.text_to_repeat_dict(text)

            command.data.repeat = command_interpreter.parse_repeat(repeat_dict, command.data.date_range.start_date,
                                                                   command.data.date_range.end_date)

        while self.current_command_index < len(self.commands_to_process):
            command = self.commands_to_process[self.current_command_index]
            user_schedule.perform_command(command)
            self.current_command_index += 1

        self.show_next_command()  # Show the next command
    '''
    def _cleanup(self, _):
        self.commands_to_process = []
        self.current_command_index = 0

    # function converts text from TextInput into a dictionary
    # so it can be sent to command_interpreter.parse_repeat
    def text_to_repeat_dict(self, text: str):
        if not text:
            return None

        text = text.lower().strip()

        pattern = None
        duration = None

        pattern_match = re.search(r"every (day|week|month|year)", text)
        if pattern_match:
            pattern = f"every {pattern_match.group(1)}"


        if "forever" in text:
            duration = "forever"

        elif re.search(r"\d+\s*times", text):
            duration = re.search(r"\d+\s*times", text).group(0)

        elif "until" in text:
            match = re.search(r"until (.+)", text)
            if match:
                duration = f"until {match.group(1).strip()}"

        return {
            "pattern": pattern,
            "duration": duration
        }