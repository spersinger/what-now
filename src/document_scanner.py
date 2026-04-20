from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.progressbar import ProgressBar
from typing import Optional



from ui import *

import time
import pytesseract
import re
# this is for windows to find pytesseract
#it does it differently than linux
#we need to have pytesseract inside the what-now folder
import sys
from pathlib import Path
import datetime
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).resolve().parent.parent / relative_path

if sys.platform.startswith("win"):
    pytesseract.pytesseract.tesseract_cmd = str(
        resource_path("pytesseract/tesseract.exe")
    )




import numpy as np
import cv2
from PIL import Image
import logging
from threading import Thread
from globals import *

from kivy.clock import Clock

# Cycling label for loading gen AI response
class CyclingLabel(Label):
    def __init__(self, messages, **kwargs):
        super().__init__(**kwargs)
        self.messages = messages
        self.current_index = 0
        self.text = messages[0]
        self.event = Clock.schedule_interval(self.cycle_text, 10)
    
    def cycle_text(self, dt):
        self.current_index = (self.current_index + 1) % len(self.messages)
        self.text = self.messages[self.current_index]
    
    def stop(self):
        self.event.cancel()

# Main class, extending from whatnow.kv CameraClick class
class DocumentScanner(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Text scanned from OCR
        self.scanned_text = None or ""

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
            "duration": duration}

        # Popup inits for verifying OCR text and AI processing
        self.verify_text_popup = ThemedPopup
        self.processing_popup = ThemedPopup
        self.accept_event_popup = ThemedPopup

        self.extracted_json = Optional[str]



    # TODO: Actually implement this, as it stands upload is completely broken because I can't test it on my computer due to my broken touchscreen.
    def upload(self):
        '''
        Function to upload images from a camera roll or desktop
        '''
        chooser = FileChooserIconView(filters=['*.png', '*.jpg', '*.jpeg', '*.pdf', '*.docx'])
        btn = PrimaryButton(text="Select", size_hint_y=None, height=40)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(chooser)
        layout.add_widget(btn)

        popup = ThemedPopup(title="Select Image", content=layout,
                      size_hint=(0.9, 0.9))

        btn.bind(on_release=lambda *a: self.load_file(chooser, popup))
        popup.open()

    def load_file(self, chooser, popup):
        if not chooser.selection:
            return

        file_path = chooser.selection[0]
        popup.dismiss()

        text = None

        # -------------------------
        # IMAGE (existing behavior)
        # -------------------------
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            text = self.ocr_image(file_path)  # assuming you already have this

        # -------------------------
        # PDF
        # -------------------------
        elif file_path.lower().endswith('.pdf'):
            from PyPDF2 import PdfReader

            reader = PdfReader(file_path)
            pages = []

            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    pages.append(extracted)

            text = "\n".join(pages)

        # -------------------------
        # DOCX
        # -------------------------
        elif file_path.lower().endswith('.docx'):
            from docx import Document

            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

            text = "\n".join(paragraphs)

        else:
            print("Unsupported file type")
            return

        # -------------------------
        # PASS TO YOUR PIPELINE
        # -------------------------
        self.scanned_text = text
        if text:
            self.build_verify_popup_ui()
            self.verify_text_popup.open()

    def capture(self):
            ################################
            ## TODO : This will go to CommandInterpreter
            #################################

            # Disable buttons while processing takes place to disallow misinputs
            self.ids.scan_button.disabled = True
            self.ids.upload_button.disabled = True

            # Do OCR, possibly move this to another function at some point
            timestr = time.strftime("%Y%m%d_%H%M%S")

            camera = self.ids['camera']

            camera.export_to_png("IMG_{}.png".format(timestr))

            # Change this to actual scan at some point, it will work the same
            original_img = cv2.imread("IMG_{}.png".format(timestr), cv2.IMREAD_GRAYSCALE)
            deskewed_img = deskew_image(original_img)
            processed_img = enhance_preprocessing(deskewed_img)
            # Save for dev purposes
            cv2.imwrite("pngs/ocr.png", processed_img)

            # Scan text using pytesseract
            self.scanned_text = pytesseract.image_to_string(
                processed_img,
                config="--oem 1 --psm 12"
            )

            # Disable camera while processing
            self.ids.camera.play = False
            self.ids.camera.opacity = 0

            # Build content for the verification popup, move this to a seperate function
            self.build_verify_popup_ui()
            self.verify_text_popup.open()

    def on_verify_finish(self):
        self.verify_text_popup.dismiss()
        self.build_processing_popup_ui()
        self.processing_popup.open()
        if self.scanned_text != None:
            thread = Thread(
                target=self._generate_commands_thread,
                args=(self.scanned_text,)
            )
            thread.daemon = True
            thread.start()

    def _generate_commands_thread(self, scanned_text):
        command_interpreter.generate_commands_from_syllabus(scanned_text)
        cmd_list = command_interpreter.commands
        command_interpreter.commands = []
        Clock.schedule_once(lambda dt: self._on_commands_ready(cmd_list))

    def _on_commands_ready(self, cmd_list):
        print("On commands ready!")
        self.processing_popup.dismiss()
        self.commands_to_process = cmd_list
        self.current_command_index = 0
        self.show_next_command()

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

    def build_accept_command_ui_popup(self, command):
        today = datetime.date.today()
        inputs = {}

        def make_label(text, **kwargs):
            return Label(text=text, size_hint_y=None, height=28,
                         halign='left', valign='middle', **kwargs)

        def make_spinner_row(values, default):
            s = ThemedSpinner(text=default, values=values,
                              size_hint=(1, None), height=40)
            return s

        # Root layout
        root = BoxLayout(orientation='vertical', spacing=6, padding=10)
        scroll = ScrollView(size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', spacing=8, padding=[0, 0, 0, 10],
                           size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        scroll.add_widget(layout)

        months = [str(m) for m in range(1, 13)]
        days   = [str(d) for d in range(1, 32)]
        years  = [str(y) for y in range(today.year, today.year + 5)]
        hours   = [str(h) for h in range(1, 13)]
        minutes = [f"{m:02d}" for m in range(0, 60, 5)]
        ampm    = ["AM", "PM"]

        # ── Command Type ──────────────────────────────────────────
        layout.add_widget(make_label("Command Type"))
        freq_row = BoxLayout(orientation='horizontal', spacing=4,
                             size_hint_y=None, height=40)
        type_options = ["ADD", "DELETE", "EDIT"]
        type_buttons = {}
        for opt in type_options:
            tb = ThemedToggleButton(text=opt, group='cmd_type', size_hint=(1, None), height=40)
            if opt == command.c_type.name:
                tb.state = 'down'
            type_buttons[opt] = tb
            freq_row.add_widget(tb)
        layout.add_widget(freq_row)

        # Fake TextInput to satisfy inputs["type"] contract
        type_input = TextInput(text=command.c_type.name, size_hint_y=None, height=0, opacity=0)
        layout.add_widget(type_input)
        inputs["type"] = type_input

        def on_type_change(instance, value):
            for opt, tb in type_buttons.items():
                if tb.state == 'down':
                    type_input.text = opt
                    break

        for tb in type_buttons.values():
            tb.bind(state=on_type_change)

        # ── Name ─────────────────────────────────────────────────
        layout.add_widget(make_label("Event Name *"))
        if command.c_type == CommandType.EDIT:
            _, new_event = command.data
            name_val = new_event.name or ""
        else:
            name_val = command.data.name or ""
        name_input = TextInput(hint_text="e.g. Intro to Computing",
                               text=name_val,
                               multiline=False, size_hint_y=None, height=40)
        layout.add_widget(name_input)
        inputs["name"] = name_input

        # ── Fields only for ADD / EDIT ────────────────────────────
        if command.c_type in (CommandType.ADD, CommandType.EDIT):
            ev = command.data[1] if command.c_type == CommandType.EDIT else command.data

            # Description
            layout.add_widget(make_label("Description"))
            desc_input = TextInput(hint_text="Optional",
                                   text=str(ev.description) if ev.description else "",
                                   multiline=False, size_hint_y=None, height=40)
            layout.add_widget(desc_input)
            inputs["desc"] = desc_input

            # Start Date
            layout.add_widget(make_label("Start Date *"))
            date_row = BoxLayout(orientation='horizontal', spacing=4,
                                 size_hint_y=None, height=40)
            if ev.date_range and ev.date_range.start_date:
                sd = ev.date_range.start_date
                dm, dd, dy = str(sd.month), str(sd.day), str(sd.year)
            else:
                dm, dd, dy = str(today.month), str(today.day), str(today.year)
            month_sp = make_spinner_row(months, dm)
            day_sp   = make_spinner_row(days,   dd)
            year_sp  = make_spinner_row(years,  dy)
            for sp in [month_sp, day_sp, year_sp]:
                date_row.add_widget(sp)
            layout.add_widget(date_row)

            # Start Time
            layout.add_widget(make_label("Start Time *"))
            start_time_row = BoxLayout(orientation='horizontal', spacing=4,
                                       size_hint_y=None, height=40)
            if ev.time_range and ev.time_range.start_time:
                st = ev.time_range.start_time
                sh = str(st.hour % 12 or 12)
                sm = f"{st.minute:02d}"
                sap = "AM" if st.hour < 12 else "PM"
            else:
                sh, sm, sap = "9", "00", "AM"
            start_h  = make_spinner_row(hours,   sh)
            start_m  = make_spinner_row(minutes, sm)
            start_ap = make_spinner_row(ampm,    sap)
            for sp in [start_h, start_m, start_ap]:
                start_time_row.add_widget(sp)
            layout.add_widget(start_time_row)

            # End Time
            layout.add_widget(make_label("End Time *"))
            end_time_row = BoxLayout(orientation='horizontal', spacing=4,
                                     size_hint_y=None, height=40)
            if ev.time_range and ev.time_range.end_time:
                et = ev.time_range.end_time
                eh = str(et.hour % 12 or 12)
                em = f"{et.minute:02d}"
                eap = "AM" if et.hour < 12 else "PM"
            else:
                eh, em, eap = "10", "00", "AM"
            end_h  = make_spinner_row(hours,   eh)
            end_m  = make_spinner_row(minutes, em)
            end_ap = make_spinner_row(ampm,    eap)
            for sp in [end_h, end_m, end_ap]:
                end_time_row.add_widget(sp)
            layout.add_widget(end_time_row)

            # Repeat frequency
            layout.add_widget(make_label("Repeat"))
            rep_freq_row = BoxLayout(orientation='horizontal', spacing=4,
                                     size_hint_y=None, height=40)
            freq_options = ["Never", "Daily", "Weekly", "Monthly"]
            freq_buttons = {}

            current_freq = "Never"
            if ev.repeat:
                cycle = str(ev.repeat.cycle).lower()
                if "week" in cycle:   current_freq = "Weekly"
                elif "day" in cycle:  current_freq = "Daily"
                elif "month" in cycle: current_freq = "Monthly"

            for opt in freq_options:
                tb = ThemedToggleButton(text=opt, group='freq_cmd', size_hint=(1, None), height=40)
                if opt == current_freq:
                    tb.state = 'down'
                freq_buttons[opt] = tb
                rep_freq_row.add_widget(tb)
            layout.add_widget(rep_freq_row)

            # Day checkboxes
            day_names = ["M", "T", "W", "Th", "F", "Sa", "Su"]
            day_map   = {"M": "m", "T": "t", "W": "w", "Th": "r", "F": "f", "Sa": "s", "Su": "u"}
            days_label = make_label("Repeat Days")
            days_row   = BoxLayout(orientation='horizontal', spacing=2,
                                   size_hint_y=None, height=40)
            day_checks = {}
            for d in day_names:
                col = BoxLayout(orientation='vertical', size_hint=(1, None), height=40)
                lbl = Label(text=d, size_hint_y=0.5)
                cb  = ThemedCheckBox(size_hint_y=0.5)
                day_checks[d] = cb
                col.add_widget(lbl)
                col.add_widget(cb)
                days_row.add_widget(col)

            end_label = make_label("Repeat Until")
            end_row   = BoxLayout(orientation='horizontal', spacing=4,
                                  size_hint_y=None, height=40)
            end_options = ["Forever", "Date"]
            end_buttons = {}
            for opt in end_options:
                tb = ThemedToggleButton(text=opt, group='repeat_end_cmd',
                                        size_hint=(1, None), height=40)
                if opt == "Forever":
                    tb.state = 'down'
                end_buttons[opt] = tb
                end_row.add_widget(tb)

            end_date_row = BoxLayout(orientation='horizontal', spacing=4,
                                     size_hint_y=None, height=40)
            end_month_sp = make_spinner_row(months, str(today.month))
            end_day_sp   = make_spinner_row(days,   str(today.day))
            end_year_sp  = make_spinner_row(years,  str(today.year))
            for sp in [end_month_sp, end_day_sp, end_year_sp]:
                end_date_row.add_widget(sp)

            error_label = Label(text="", color=(1, 0, 0, 1),
                                size_hint_y=None, height=28)

            def on_freq_change(instance, value):
                is_weekly = freq_buttons["Weekly"].state == 'down'
                is_never  = freq_buttons["Never"].state == 'down'
                for w in [days_label, days_row, end_label, end_row, end_date_row]:
                    if w.parent:
                        w.parent.remove_widget(w)
                if is_never:
                    return
                idx = layout.children.index(error_label)
                if is_weekly:
                    layout.add_widget(end_label,  index=idx)
                    layout.add_widget(end_row,    index=idx)
                    layout.add_widget(days_label, index=idx)
                    layout.add_widget(days_row,   index=idx)
                else:
                    layout.add_widget(end_label, index=idx)
                    layout.add_widget(end_row,   index=idx)

            def on_end_change(instance, value):
                if end_date_row.parent:
                    end_date_row.parent.remove_widget(end_date_row)
                if end_buttons["Date"].state == 'down':
                    idx = layout.children.index(error_label)
                    layout.add_widget(end_date_row, index=idx)

            for tb in freq_buttons.values():
                tb.bind(state=on_freq_change)
            for tb in end_buttons.values():
                tb.bind(state=on_end_change)

            layout.add_widget(error_label)

        elif command.c_type == CommandType.DELETE:
            # Date range (optional)
            if command.data.date_range:
                layout.add_widget(make_label("Date Range"))
                sd = command.data.date_range.start_date
                date_input = TextInput(
                    text=str(command.data.date_range),
                    multiline=False, size_hint_y=None, height=40
                )
                layout.add_widget(date_input)
                inputs["date"] = date_input

            error_label = Label(text="", color=(1, 0, 0, 1),
                                size_hint_y=None, height=28)
            layout.add_widget(error_label)

        # ── Accept / Reject buttons ───────────────────────────────
        btn_row = BoxLayout(orientation='horizontal', spacing=8,
                            size_hint_y=None, height=44)

        def on_submit(*args):
            if command.c_type in (CommandType.ADD, CommandType.EDIT):
                ev = command.data[1] if command.c_type == CommandType.EDIT else command.data

                if not name_input.text.strip():
                    error_label.text = "Event name is required."
                    return  # Prevent submission without name

                inputs["name"] = name_input

                # Build date string for on_accept_command
                date_str = f"{month_sp.text}/{day_sp.text}/{year_sp.text}"
                date_input = TextInput(text=date_str)
                inputs["date"] = date_input

                def fmt_time(h, m, ap):
                    return f"{h}:{m}{'a' if ap == 'AM' else 'p'}"

                time_str = f"{fmt_time(start_h.text, start_m.text, start_ap.text)} -> {fmt_time(end_h.text, end_m.text, end_ap.text)}"
                time_input = TextInput(text=time_str)
                inputs["time"] = time_input

                freq = next((k for k, v in freq_buttons.items() if v.state == 'down'), "Never")
                if freq != "Never":
                    day_map = {"M": "m", "T": "t", "W": "w", "Th": "r", "F": "f", "Sa": "s", "Su": "u"}
                    if freq == "Weekly":
                        selected = "".join(day_map[d] for d in day_names if day_checks[d].active)
                        rule = f"week {selected}" if selected else "week"
                    elif freq == "Daily":
                        rule = "day"
                    else:
                        rule = "month"

                    end_mode = next((k for k, v in end_buttons.items() if v.state == 'down'), "Forever")
                    repeat_end = "forever" if end_mode == "Forever" else \
                        f"until {end_month_sp.text}/{end_day_sp.text}/{end_year_sp.text}"

                    inputs["repeat_rule"] = rule
                    inputs["repeat_end"] = repeat_end

            self.on_accept_command(command, inputs)
            self.accept_command_popup.dismiss()

        accept_btn = PrimaryButton(text='Accept', size_hint=(1, None), height=44)
        accept_btn.bind(on_release=on_submit)

        reject_btn = PrimaryButton(text='Reject', size_hint=(1, None), height=44)
        reject_btn.bind(on_release=lambda x: self.on_reject_command())

        btn_row.add_widget(accept_btn)
        btn_row.add_widget(reject_btn)

        root.add_widget(scroll)
        root.add_widget(btn_row)

        self.accept_command_popup = ThemedPopup(
            title='Verify Command',
            content=root,
            size_hint=(0.9, 0.92),
            auto_dismiss=False
        )

    def on_accept_command(self, command, inputs):
        self.accept_command_popup.dismiss()

        #convert string to CommandType
        if "type" in inputs:
            text = inputs["type"].text.strip().upper()
            command.c_type = CommandType[text]

        if command.c_type.name == "EDIT":
            #all this data goes to the second event of
            #the tuple, the edit_event (NOT search_event)
            if "name" in inputs:
                command.data[1].name = inputs["name"].text

            if "desc" in inputs:
                command.data[1].description = inputs["desc"].text

            if "notif" in inputs:
                text = inputs["notif"].text
                # split the string into a list
                notif_list = [n.strip() for n in text.split(",") if n.strip()]
                # parse notification list
                command.data[1].notif_times = command_interpreter.parse_notifications(notif_list)

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
                command.data[1].date_range = CalendarEvent.DateRange(start_date, end_date)

            if "time" in inputs:
                text = inputs["time"].text
                parts = [p.strip() for p in re.split(r'\s*->\s*', text)]

                if len(parts) == 2:
                    start_t, end_t = parts
                else:
                    start_t = parts[0]
                    end_t = None

                # create time range and put it in data
                command.data[1].time_range = command_interpreter.parse_time(start_t, end_t)

            if "repeat" in inputs:
                text = inputs["repeat"].text

                repeat_dict = self.text_to_repeat_dict(text)

                start_date = command.data[1].date_range.start_date if command.data[1].date_range else None
                end_date = command.data[1].date_range.end_date if command.data[1].date_range else None
                command.data[1].repeat = command_interpreter.parse_repeat(repeat_dict, start_date, end_date)

            user_schedule.perform_command(command)

        elif command.c_type.name == "ADD" or command.c_type.name == "DELETE":
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
                command.data.date_range = DateRange(start_date,end_date)


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

            if "repeat_rule" in inputs and "repeat_end" in inputs:
                rule = inputs["repeat_rule"]
                repeat_end = inputs["repeat_end"]
                command.data.repeat = Repeat(rule, repeat_end)

            user_schedule.perform_command(command)
            print(f"DEBUG: Added event - name: {command.data.name}, date: {command.data.date_range}")

        #TODO:error handling for non-valid command:
        else:
            pass

        self.current_command_index += 1
        self.show_next_command()  # Show the next command

    def on_reject_command(self):
        self.accept_command_popup.dismiss()

        # just skip this command
        self.current_command_index += 1

        self.show_next_command()

    def build_verify_popup_ui(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=5)

        title = HeaderLabel(
            text="[b]Verify Scanned Text[/b]",
            size_hint=(1, 0.1)
        )

        text_input = TextInput(
            text=self.scanned_text,
            multiline=True,
            size_hint=(1, 0.8)
        )

        finish_btn = PrimaryButton(text='Analyze with AI', size_hint=(1, 0.1))
        finish_btn.bind(on_press=lambda x: self.on_verify_finish())

        content.add_widget(title)
        content.add_widget(text_input)
        content.add_widget(finish_btn)

        self.verify_text_popup = ThemedPopup(
            title='Verify Scanned Text',
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=False
        )

    def build_processing_popup_ui(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        processing_text = Label(text='AI scanning in progress')

        messages = [
            "Loading text...",
            "Loading models...",
            "Extracting events with AI...",
            "Analyzing output...",
            "Error checking...",
            "Testing results...",
            "Finishing up...",
            "Connecting the dots...",
            "Almost done..."
            "Just a moment...",
            "Hang tight...",
        ]

        cycling_label = CyclingLabel(messages)

        progress_bar = ProgressBar(max=100, size_hint=(1, None), height=30)
        # Animation to fake loading since we don't actually know the status of the AI
        anim = Animation(value=100, duration=10) + Animation(value=0, duration=0)
        anim.repeat = True

        content.add_widget(cycling_label)
        content.add_widget(progress_bar)

        self.processing_popup = Popup(
            title='Processing',
            content=content,
            size_hint=(1, 1),
            auto_dismiss=False  # Prevent manual dismissal
        )

        anim.start(progress_bar)

    def _cleanup(self, _):
        self.commands_to_process = []
        self.current_command_index = 0

