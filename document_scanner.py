from image_scanner import *

from kivy.uix.boxlayout import BoxLayout
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

import time
import pytesseract
import numpy as np
import cv2
from PIL import Image
import logging
from threading import Thread

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
# TODO: Rename in the future, CameraClick isn't too descriptive, possible CameraScanner?
class DocumentScanner(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Text scanned from OCR
        self.scanned_text = Optional[str]

        # Popup inits for verifying OCR text and AI processing
        self.verify_text_popup = Optional[Popup]
        self.processing_popup = Optional[Popup] 
        self.accept_event_popup = Optional[Popup]

        # Gen AI parser
        self.parser = LocalSyllabusParser()
        self.extracted_json = Optional[str]

    def capture(self):
            # Disable camera while processing
            ################################
            ## TODO : This will go to CommandInterpreter
            #################################
            self.ids.camera.play = False
            self.ids.camera.opacity = 0

            # Disable buttons while processing takes place to disallow misinputs
            self.ids.scan_button.disabled = True
            self.ids.upload_button.disabled = True

            # Do OCR, possibly move this to another function at some point
            timestr = time.strftime("%Y%m%d_%H%M%S")
            file_name = f"IMG_{timestr}.png"

            # Change this to actual scan at some point, it will work the same
            original_img = cv2.imread("test_original.png", cv2.IMREAD_GRAYSCALE)
            deskewed_img = deskew_image(original_img)
            processed_img = enhance_preprocessing(deskewed_img)
            # Save for dev purposes
            cv2.imwrite("ocr.png", processed_img)

            # Scan text using pytesseract
            self.scanned_text = pytesseract.image_to_string(
                processed_img,
                config="--oem 1 --psm 12"
            )

            # Build content for the verification popup, move this to a seperate function
            self.build_verify_popup_ui()
            self.verify_text_popup.open()


    # Gen AI thread worker
    def _capture_worker(self):
            try:
                result = self.parser.parse(self.scanned_text)
                self.extracted_json = result
                Clock.schedule_once(self._extract_json)

            except Exception as e:
                print(e)
                Clock.schedule_once(self._cleanup)

    # This will be for validating the events the AI generates
    # A popup will come up for each event and the user will be able to change details if they are incorrect, press accept, or accept all
    def _extract_json(self, _):
        self.processing_popup.dismiss()

        self.events_to_process = list(self.extracted_json.get("recurring_events", []))
        self.events_to_process.extend(self.extracted_json.get("exams", []))
        self.events_to_process.extend(self.extracted_json.get("assignments", []))

        self.current_event_index = 0
    
        if self.events_to_process:
            self.show_next_event()
        else:
            print("No events to process")

    def show_next_event(self):
        if self.current_event_index < len(self.events_to_process):
            event = self.events_to_process[self.current_event_index]
            self.build_accept_event_ui_popup(event)
            self.accept_event_popup.open()

        else:
            # All events processed
            print("Exams: " + str(self.extracted_json.get("exams", [])))
            print("Homework: " + str(self.extracted_json.get("assignments", [])))
            Clock.schedule_once(self._cleanup)

    def on_accept_event(self):
        self.accept_event_popup.dismiss()
        self.current_event_index += 1
        self.show_next_event()  # Show the next event

    def on_accept_all_event(self):
        self.accept_event_popup.dismiss()
        self.current_event_index = len(self.events_to_process)
        self.show_next_event()  # Show the next event
    
    def _cleanup(self, _):

        # TODO: Fix upload button, it is disabled currently since it doesn't work lol
        self.ids.upload_button.disabled = True
        self.ids.scan_button.disabled = False
        self.ids.camera.opacity = 100
        self.ids.camera.play = True

    def on_verify_finish(self):
        self.verify_text_popup.dismiss()

        self.build_processing_popup_ui()

        self.processing_popup.open()

        # Run gen AI in seperate thread so that the app doesn't hang lol
        Thread(target=self._capture_worker, daemon=True).start()

    ########################
    ### UI BUILDER FUNCTIONS
    ########################

    def build_accept_event_ui_popup(self, event):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        button_box = BoxLayout(orientation='horizontal', padding=10, spacing=10)

        if (event.get('due_day')):
            # Assignment
            name_label = Label(text='Name:', size_hint_y=None, height=30, halign='left')
            name_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
            name_text_input = TextInput(
                text=str(event.get('name')),
                multiline=True,
                size_hint_x=1,
                size_hint_y=None,
                height=30
            )
            
            due_day_label = Label(text='Due Day:', size_hint_y=None, height=30, halign='left')
            due_day_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
            due_day_input = TextInput(
                text=str(event.get('due_day')),
                multiline=True,
                size_hint_x=1,
                size_hint_y=None,
                height=30
            )
            
            due_time_label = Label(text='Due Time:', size_hint_y=None, height=30, halign='left')
            due_time_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
            due_time_input = TextInput(
                text=str(event.get('due_time')),
                multiline=True,
                size_hint_x=1,
                size_hint_y=None,
                height=30
            )
            
            content.add_widget(name_label)
            content.add_widget(name_text_input)

            content.add_widget(due_day_label)
            content.add_widget(due_day_input)

            content.add_widget(due_time_label)
            content.add_widget(due_time_input)

        else:
            # Recurring event or exam
            name_label = Label(text='Name:', size_hint_y=None, height=30, halign='left')
            name_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
            name_text_input = TextInput(
                text=str(event.get('name')),
                multiline=True,
                size_hint_x=1,
                size_hint_y=None,
                height=30
            )
            
            day_label = Label(text='Day:', size_hint_y=None, height=30, halign='left')
            day_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
            day_of_week_input = TextInput(
                text=str(event.get('day')),
                multiline=False,
                size_hint_x=1,
                size_hint_y=None,
                height=30
            )
            
            start_time_label = Label(text='Start Time:', size_hint_y=None, height=30, halign='left')
            start_time_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
            start_time_input = TextInput(
                text=str(event.get('start_time')),
                multiline=False,
                size_hint_x=1,
                size_hint_y=None,
                height=30
            )
            
            end_time_label = Label(text='End Time:', size_hint_y=None, height=30, halign='left')
            end_time_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
            end_time_input = TextInput(
                text=str(event.get('end_time')),
                multiline=False,
                size_hint_x=1,
                size_hint_y=None,
                height=30 
            )
            
            room_label = Label(text='Room:', size_hint_y=None, height=30, halign='left')
            room_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
            room_input = TextInput(
                text=str(event.get('room')),
                multiline=False,
                size_hint_x=1,
                size_hint_y=None,
                height=30
            )
            
            content.add_widget(name_label)
            content.add_widget(name_text_input)

            content.add_widget(day_label)
            content.add_widget(day_of_week_input)

            content.add_widget(start_time_label)
            content.add_widget(start_time_input)

            content.add_widget(end_time_label)
            content.add_widget(end_time_input)

            content.add_widget(room_label)
            content.add_widget(room_input)

        accept_btn = Button(text='Accept', size_hint=(1, 0.1))
        accept_btn.bind(on_press=lambda x: self.on_accept_event())

        accept_all_btn = Button(text='Accept all', size_hint=(1, 0.1))
        accept_all_btn.bind(on_press=lambda x: self.on_accept_all_event())

        button_box.add_widget(accept_btn)
        button_box.add_widget(accept_all_btn)

        content.add_widget(button_box)

        self.accept_event_popup = Popup(
            title='Verify Scanned Text',
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=False
        )

    def build_verify_popup_ui(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        text_input = TextInput(
            text=self.scanned_text,
            multiline=True,
            size_hint=(1, 0.8)
        )

        finish_btn = Button(text='Analyze with AI', size_hint=(1, 0.1))
        finish_btn.bind(on_press=lambda x: self.on_verify_finish())

        content.add_widget(text_input)
        content.add_widget(finish_btn)

        self.verify_text_popup = Popup(
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

    # TODO: Actually implement this, as it stands upload is completely broken because I can't test it on my computer due to my broken touchscreen.
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

