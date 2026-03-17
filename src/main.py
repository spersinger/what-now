try:
    from kivy.app import App
except ModuleNotFoundError:
    print("\nKivy was not found. Possible issues:")
    print("\t- python3.13 not used. check with `python --verison` and run `source setup.sh`")
    print("\t- kivy was never installed. run `source setup.sh` to check, install, or view install errors.")
    quit()
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.config import Config

import calendar
from datetime import date

Builder.load_file('../ui/themed.kv')
Builder.load_file('../ui/home_page.kv')
Builder.load_file('../ui/voice_page.kv')
Builder.load_file('../ui/scanner_page.kv')
Builder.load_file('../ui/whatnow.kv')

Config.set('kivy', 'camera', 'opencv')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('kivy', 'keyboard_mode', 'system')

# For fixing multitouch
Config.remove_option('input', '%(name)s')
Config.set('input', 'mouse', 'mouse')

# custom class imports
from CalendarEvent import CalendarEvent
from Schedule import Schedule
from Command import CommandInterpreter
from Voice import Voice
from document_scanner import DocumentScanner
from ui import *


# global data objects: schedule, command interpreter
user_schedule = Schedule()
command_interpreter = CommandInterpreter()


class Home(Screen):
    # Possibly move these into their own file? Unsure

    def build_calendar(self, year, month):
        grid = self.ids.calendar_grid
        grid.clear_widgets()
        today = date.today().day

        # leading empty cells
        first_weekday = calendar.monthrange(year, month)[0]  # 0=Mon, so adjust for Sun start
        start_offset = (first_weekday + 1) % 7
        for _ in range(start_offset):
            grid.add_widget(Widget(size_hint_y=None, height=30))

        for day in range(1, calendar.monthrange(year, month)[1] + 1):
            if day == today:
                cell = CalendarDayToday(day_text=str(day))
            else:
                color = [0.333, 0.333, 0.333, 1] if ... else [1, 1, 1, 1]  # gray weekends
                cell = CalendarDayCell(day_text=str(day), day_color=color)
            grid.add_widget(cell)

    def build_events(self, events):
        box = self.ids.events_box
        box.clear_widgets()
        for i, ev in enumerate(events):
            if i > 0:
                box.add_widget(Widget(size_hint_y=None, height=1))  # divider
            box.add_widget(EventItem(
                event_type=ev['type'],
                event_name=ev['name'],
                event_time=ev['time']
            ))
    def on_kv_post(self, base_widget):
        today = date.today()
        self.build_calendar(today.year, today.month)
        ## TODO: FIX
        events = [
            {
                'type': 'Lecture',
                'name': 'Intro to Computing',
                'time': '10:00AM-11:15AM'
            },
            {
                'type': 'Office Hours',
                'name': 'Intro to Computing',
                'time': '1:00PM-3:00PM'
            },
        ]

        self.build_events(events)

class Voice(Screen): pass

class Scanner(Screen):
    def on_enter(self):
        self.ids.cam_view.ids.camera.play = True

    def on_leave(self):
        self.ids.cam_view.ids.camera.play = False

class Edit(Screen): pass
class Root(BoxLayout):
    # TODO, fix this, it is janky but works.
    # The issue is that passing arguments from a .kv file is sorta hit or miss
    # so I hard code the screen_name onto the buttons, and then just 
    # don't use the screen name that is passed? I actually don't entirely know 
    # why this works, but it does so...
    def set_active(self, screen_name):
        sm = self.ids.sm
        # I guess this works here? Unsure why since printing screen name gives us
        # nothing, but it still switches the screen with sm (screen manager id)
        sm.current = screen_name

        for btn_id, name in (
            ("home_button", "Home"),
            ("voice_button", "Voice"),
            ("scanner_button", "Scanner"),
        ):
            btn = self.ids[btn_id]

            if btn.screen_name == screen_name:
                btn.text = f"[b]{name}[/b]"
                btn.color = (1, 1, 1, 1)  # selected color
            else:
                btn.text = name
                btn.color = (0.6, 0.6, 0.6, 1)  # unselected color

class WhatNow(App):
    def build(self):
        self.title = "What Now?"
        # string for voice input to be used by command interpreter
        self.voice_input = ""
        return Root()


if __name__ == "__main__":
    WhatNow().run()
