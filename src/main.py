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
from CalendarEvent import *
from Schedule import Schedule
from Command import CommandInterpreter
from Voice import Voice
from document_scanner import DocumentScanner
from ui import *


# global data objects: schedule, command interpreter
user_schedule = Schedule()
command_interpreter = CommandInterpreter()

class Home(Screen):

    def add_event(self, event: CalendarEvent):
        user_schedule.add_event(event)
        self.refresh()

    def refresh(self):
        today = date.today()
        self.build_calendar(today.year, today.month)
        self.build_events(user_schedule.get_for_date(date.today()))

    def build_calendar(self, year, month):
        grid = self.ids.calendar_grid
        grid.clear_widgets()
        today = date.today().day
        first_weekday = calendar.monthrange(year, month)[0]
        start_offset = (first_weekday + 1) % 7
        for _ in range(start_offset):
            grid.add_widget(Widget(size_hint_y=None, height=30))

        event_days = user_schedule.get_days_with_events(year, month)  # <-- updated

        for day in range(1, calendar.monthrange(year, month)[1] + 1):
            if day == today:
                cell = CalendarDayToday(day_text=str(day))
            else:
                color = [0.333, 0.333, 0.333, 1] if ... else [1, 1, 1, 1]
                cell = CalendarDayCell(day_text=str(day), day_color=color, has_event=day in event_days)
            grid.add_widget(cell)

    def build_events(self, events):
        box = self.ids.events_box
        box.clear_widgets()
        if len(events) == 0:
            box.add_widget(EventItem(
                event_type='No Events Today! Enjoy your day off!',
                event_name="",
                event_time="",
                event_date=""
            ))
        else:
            for i, ev in enumerate(events):
                if i > 0:
                    box.add_widget(Widget(size_hint_y=None, height=1))
                box.add_widget(EventItem(
                    event_type='Lecture',
                    event_name=ev.name,
                    event_time=str(ev.time_range.start_time) + " - " + str(ev.time_range.end_time),
                    event_date=""
                ))

    def on_kv_post(self, base_widget):
        self.add_event(CalendarEvent(
            name="Intro to Computing",
            desc="Intro to Computing class",
            notifs=None,
            dates=DateRange("3/2"),
            times=TimeRange("9:00a", "10:00a"),
            repeat=Repeat("week mwf", "forever")
        ))
        self.add_event(CalendarEvent(
            name="Language Translation",
            desc="Language Translation class",
            notifs=None,
            dates=DateRange("3/2"),
            times=TimeRange("12:30p", "1:45p"),
            repeat=Repeat("week tr", "forever")
        ))

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
