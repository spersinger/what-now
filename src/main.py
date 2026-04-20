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
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from datetime import date as dt_date

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.config import Config
from kivy.clock  import Clock
import asyncio

from icalendar import Calendar, Event
from datetime import datetime
from datetime import time
import json

import sys
import os


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), relative_path)

import calendar
import datetime
from datetime import date

Builder.load_file(resource_path('ui/themed.kv'))
Builder.load_file(resource_path('ui/home_page.kv'))
Builder.load_file(resource_path('ui/voice_page.kv'))
Builder.load_file(resource_path('ui/scanner_page.kv'))
Builder.load_file(resource_path('ui/whatnow.kv'))


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
from Voice import Voice
from document_scanner import DocumentScanner
from ui import *
from globals import user_schedule, command_interpreter
from kivy.uix.camera import Camera
from kivy.clock import Clock


import calendar

# TODO: Move to seperate file
class Home(Screen):
    view_type = "month"

    def add_event(self, event: CalendarEvent):
        user_schedule.add_event(event)
        self.refresh()

    def refresh(self):
        today = date.today()
        self.ids.calendar_month_label.text = "[b]" + today.strftime("%B") + "[/b]"
        if self.view_type == "month":
            self.build_calendar(today.year, today.month)
        else:
            self.build_week_calendar()

        self.build_events(user_schedule.get_for_date(date.today()))

    def toggle_view(self):
        if self.view_type == "month":
            self.view_type = "week"
            self.ids.change_view_type_button.text = "[b]Month View[/b]"
            self.ids.events_box_header_label.text = "[b]This Weeks Events[/b]"

            # If weekend (Sat=5, Sun=6), show next week; otherwise show current week
            today = date.today()
            weekday = today.weekday()  # Mon=0 ... Sun=6
            if weekday >= 5:
                # Jump to next Monday
                days_until_monday = 7 - weekday
                week_start = today + timedelta(days=days_until_monday)
            else:
                # Start of current week (Monday)
                week_start = today - timedelta(days=weekday)

            week_days = [week_start + timedelta(days=i) for i in range(7)]
            all_events = []
            for d in week_days:
                all_events.extend(user_schedule.get_for_date(d))
            self.build_events(all_events)

            self.build_week_calendar()
        else:
            self.view_type = "month"
            self.ids.change_view_type_button.text = "[b]Week View[/b]"
            today = date.today()
            self.ids.events_box_header_label.text = "[b]Today's Events[/b]"
            self.build_calendar(today.year, today.month)

    def _sync_grid_row_heights(self, grid):
        children = list(grid.children)
        if not children:
            return
        cols = 7
        num_rows = len(children) // cols
        for row in range(num_rows):
            row_start = row * cols
            row_end = row_start + cols
            row_cells = children[row_start:row_end]
            max_height = max((c.height for c in row_cells), default=0)
            for c in row_cells:
                c.height = max_height
                c.pos_hint = {'top': 1}

    def build_week_calendar(self):
        from datetime import timedelta
        grid = self.ids.calendar_grid
        grid.clear_widgets()

        today = date.today()

        # If weekend (Sat=5, Sun=6), show next week; otherwise show current week
        weekday = today.weekday()  # Mon=0 ... Sun=6
        if weekday >= 5:
            # Jump to next Monday
            days_until_monday = 7 - weekday
            week_start = today + timedelta(days=days_until_monday)
        else:
            # Start of current week (Monday)
            week_start = today - timedelta(days=weekday)

        week_days = [week_start + timedelta(days=i) for i in range(7)]

        # Day-of-week headers
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for name in day_names:
            grid.add_widget(Label(
                text=name,
                size_hint_y=None,
                height=20,
                font_size='11sp',
                color=(0.6, 0.6, 0.6, 1)
            ))

        # Day cells
        events = {}
        for d in week_days:
            event_d = user_schedule.get_for_date(d)
            events[d.day] = event_d

        for d in week_days:
            events_day_list = events.get(d.day, 0)
            sorted_day_events = sorted(
                events_day_list,
                key=lambda ev: ev.time_range.start_time if ev.time_range and ev.time_range.start_time else datetime.time.max
            )

            if d == today:
                cell = CalendarDayToday(day_text=str(d.day), event_count=len(events_day_list), events=sorted_day_events)
            else:
                color = [1, 1, 1, 1]
                cell = CalendarDayCell(day_text=str(d.day), day_color=color, event_count=len(events_day_list), events=sorted_day_events)
            grid.add_widget(cell)

        # Sync heights for all rows
        Clock.schedule_once(lambda dt: self._sync_grid_row_heights(grid))

        # Show events for the whole week in the events box
        all_events = []
        for d in week_days:
            all_events.extend(user_schedule.get_for_date(d))
        self.build_events(all_events)

    def build_calendar(self, year, month):
        grid = self.ids.calendar_grid
        grid.clear_widgets()
        today = datetime.date.today().day
        first_weekday = calendar.monthrange(year, month)[0]
        start_offset = (first_weekday + 1) % 7
        for _ in range(start_offset):
            grid.add_widget(Widget(size_hint_y=None, height=30))

        event_counts = user_schedule.get_event_counts(year, month)

        for day in range(1, calendar.monthrange(year, month)[1] + 1):
            count = event_counts.get(day, 0)
            current_date = Date(year, month, day)
            events = user_schedule.get_for_date(current_date)
            sorted_events = sorted(
                events,
                key=lambda ev: ev.time_range.start_time if ev.time_range and ev.time_range.start_time else datetime.time.max
            )

            if day == today:
                cell = CalendarDayToday(day_text=str(day), event_count=count, events=sorted_events)
            else:
                color = [0.333, 0.333, 0.333, 1] if ... else [1, 1, 1, 1]
                cell = CalendarDayCell(day_text=str(day), day_color=color, event_count=count, events=sorted_events)

            grid.add_widget(cell)

        Clock.schedule_once(lambda dt: self._sync_grid_row_heights(grid))

    def build_events(self, events):
        box = self.ids.events_box
        box.clear_widgets()
        if len(events) == 0:
            box.add_widget(EventItem(
                event_name="No Events Today! Enjoy your day off!",
                event_time="",
                event_date=""
            ))
        else:
            sorted_events = sorted(
                events,
                key=lambda ev: ev.time_range.start_time if ev.time_range and ev.time_range.start_time else datetime.time.max
            )

            for i, ev in enumerate(sorted_events):
                if i > 0:
                    box.add_widget(Widget(size_hint_y=None, height=1))

                day, date = ev.date_range.start_date.strftime("%A"), ev.date_range.start_date
                edit_event = EditEventItem(
                    event_name=ev.name,
                    event_time=str(ev.time_range.start_time) + " - " + str(ev.time_range.end_time),
                    event_date=f"{day} - {date}"
                )
                edit_event.set_event(ev)
                box.add_widget(edit_event)

    def on_kv_post(self, base_widget):
        # refresh screen to get loaded events
        self.refresh()

        search_event_btn = self.ids.search_event_button
        search_event_btn.bind(on_release=lambda *a: self.search_event_popup())
        add_event_btn = self.ids.add_event_button
        add_event_btn.bind(on_release=lambda *a: self.add_event_popup())
        save_btn = self.ids.save_button
        save_btn.bind(on_release=lambda *a: self.save_current_schedule())
        change_view_type_btn = self.ids.change_view_type_button
        change_view_type_btn.bind(on_release=lambda *a: self.toggle_view())

        user_schedule.notify_daily()
        # Schedule notifications for today
        user_schedule.setup_notification_callbacks()

        # Every 24 hours
        now = datetime.datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        seconds_until_midnight = ((midnight - now).seconds + 86400) % 86400

        # Schedule notifications at next midnight so we don't miss any
        Clock.schedule_once(
            lambda *a: (
                user_schedule.setup_notification_callbacks(),
                # Then schedule at next midnight
                Clock.schedule_interval(lambda *a: user_schedule.setup_notification_callbacks(), 86400)
            ),
            seconds_until_midnight
        )

    def search_event_popup(self):
        '''
        Popup to create and add a new CalendarEvent.
        - Scroll wheel pickers for date and time
        - Checkboxes for repeat days
        - Toggle buttons for repeat frequency / end
        '''
        root = BoxLayout(orientation='vertical', spacing=6, padding=10)
        scroll = ScrollView(size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', spacing=8, padding=[0, 0, 0, 10],
                           size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        layout.add_widget(Widget(size_hint_y=None, height=1))

        scroll.add_widget(layout)

        search_bar = BoxLayout(orientation='horizontal', spacing=6, padding=10)
        name_input = TextInput(hint_text="e.g. Intro to Computing",
                               multiline=False, size_hint_y=None, height=40)
        search_button = PrimaryButton(text="Search", size_hint_x=0.15,
                                      size_hint_y=None, height=44)

        root.add_widget(Label(text="Event Name *", size_hint_y=None, height=28,
                              halign='left', valign='middle'))
        search_bar.add_widget(name_input)
        search_bar.add_widget(search_button)
        root.add_widget(search_bar)
        root.add_widget(scroll)
        search_button.bind(on_release=lambda *a: self.search_events(name_input.text, layout))

        popup = ThemedPopup(title="", content=root, size_hint=(0.9, 0.92))
        popup.open()

    def search_events(self, search_term, layout):
        search_event = CalendarEvent(
                name= search_term,
                desc= None,
                notifs= None,
                dates= DateRange(datetime.date.today(), datetime.date.today()),
                times= None,
                repeat= None,
                )
        result = user_schedule.search_events(search_event)
        if result is None:
            layout.add_widget(EventItem(
                event_name="No events found!",
                event_time="",
                event_date=""
            ))
        else:
            ev, g_idx, e_idx = result  # unpack the tuple
            day, date = ev.date_range.start_date.strftime("%A"), ev.date_range.start_date
            edit_event = EditEventItem(
                event_name=ev.name,
                event_time=str(ev.time_range.start_time) + " - " + str(ev.time_range.end_time),
                event_date=f"{day} - {date}"
            )
            edit_event.set_event(ev)
            layout.add_widget(edit_event)


    def save_current_schedule(self):
        events = user_schedule.get_first_events()  # flatten all event groups
        try:
            user_schedule.save_to_ics(events)  # your already implemented save function
            popup = ThemedPopup(
                title="Saved",
                content=Label(text="Schedule saved"),
                size_hint=(0.6, 0.3)
            )
            popup.open()
        except Exception as e:
            popup = ThemedPopup(
                title="Error",
                content=Label(text=f"Failed to save schedule:\n{str(e)}"),
                size_hint=(0.6, 0.3)
            )
            popup.open()

    def add_event_popup(self):
        '''
        Popup to create and add a new CalendarEvent.
        - Scroll wheel pickers for date and time
        - Checkboxes for repeat days
        - Toggle buttons for repeat frequency / end
        '''

        today = datetime.date.today()

        # Helpers

        def make_label(text, **kwargs):
            return Label(text=text, size_hint_y=None, height=28,
                         halign='left', valign='middle', **kwargs)

        def make_spinner_row(values, default):
            """A horizontal row of a single Spinner acting as a wheel picker."""
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

        # Name
        layout.add_widget(make_label("Event Name *"))
        name_input = TextInput(hint_text="e.g. Intro to Computing",
                               multiline=False, size_hint_y=None, height=40)
        layout.add_widget(name_input)

        # Description
        layout.add_widget(make_label("Description"))
        desc_input = TextInput(hint_text="Optional",
                               multiline=False, size_hint_y=None, height=40)
        layout.add_widget(desc_input)

        # Date pickers
        layout.add_widget(make_label("Start Date *"))
        months = [str(m) for m in range(1, 13)]
        days   = [str(d) for d in range(1, 32)]
        years  = [str(y) for y in range(today.year, today.year + 5)]

        date_row = BoxLayout(orientation='horizontal', spacing=4,
                             size_hint_y=None, height=40)
        month_sp = make_spinner_row(months, str(today.month))
        day_sp   = make_spinner_row(days,   str(today.day))
        year_sp  = make_spinner_row(years,  str(today.year))
        for sp in [month_sp, day_sp, year_sp]:
            date_row.add_widget(sp)
        layout.add_widget(date_row)

        # Time pickers
        hours   = [str(h) for h in range(1, 13)]
        minutes = [f"{m:02d}" for m in range(0, 60, 5)]
        ampm    = ["AM", "PM"]

        layout.add_widget(make_label("Start Time *"))
        start_time_row = BoxLayout(orientation='horizontal', spacing=4,
                                   size_hint_y=None, height=40)
        start_h  = make_spinner_row(hours,   "9")
        start_m  = make_spinner_row(minutes, "00")
        start_ap = make_spinner_row(ampm,    "AM")
        for sp in [start_h, start_m, start_ap]:
            start_time_row.add_widget(sp)
        layout.add_widget(start_time_row)

        layout.add_widget(make_label("End Time *"))
        end_time_row = BoxLayout(orientation='horizontal', spacing=4,
                                 size_hint_y=None, height=40)
        end_h  = make_spinner_row(hours,   "10")
        end_m  = make_spinner_row(minutes, "00")
        end_ap = make_spinner_row(ampm,    "AM")
        for sp in [end_h, end_m, end_ap]:
            end_time_row.add_widget(sp)
        layout.add_widget(end_time_row)

        # Notification time selector
        layout.add_widget(make_label("Notify Before"))
        notif_num_row = BoxLayout(orientation='horizontal', spacing=4,
                                  size_hint_y=None, height=40)
        notif_num_values = [str(n) for n in range(1, 61)]
        notif_num = ThemedSpinner(text="15", values=notif_num_values,
                                 size_hint=(1, None), height=40)
        notif_type_values = ["minutes", "hours", "days", "weeks"]
        notif_type = ThemedSpinner(text="minutes", values=notif_type_values,
                                   size_hint=(1, None), height=40)
        notif_num_row.add_widget(notif_num)
        notif_num_row.add_widget(notif_type)
        layout.add_widget(notif_num_row)

        # Repeat frequency toggle buttons
        layout.add_widget(make_label("Repeat"))
        freq_row = BoxLayout(orientation='horizontal', spacing=4,
                             size_hint_y=None, height=40)
        freq_options = ["Never", "Daily", "Weekly", "Monthly"]
        freq_buttons = {}
        for opt in freq_options:
            tb = ThemedToggleButton(text=opt, group='freq', size_hint=(1, None), height=40)
            if opt == "Never":
                tb.state = 'down'
            freq_buttons[opt] = tb
            freq_row.add_widget(tb)
        layout.add_widget(freq_row)

        # Day checkboxes (shown only when Weekly is selected)
        days_label = make_label("Repeat Days")
        day_names  = ["M", "T", "W", "Th", "F", "Sa", "Su"]
        day_map    = {"M": "m", "T": "t", "W": "w", "Th": "th", "F": "f",
                      "Sa": "sa", "Su": "su"}
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
            tb = ThemedToggleButton(text=opt, group='repeat_end',
                              size_hint=(1, None), height=40)
            if opt == "Forever":
                tb.state = 'down'
            end_buttons[opt] = tb
            end_row.add_widget(tb)

        # End date pickers (shown only when "Date" is selected)
        end_date_row = BoxLayout(orientation='horizontal', spacing=4,
                                 size_hint_y=None, height=40)
        end_month_sp = make_spinner_row(months, str(today.month))
        end_day_sp   = make_spinner_row(days,   str(today.day))
        end_year_sp  = make_spinner_row(years,  str(today.year))
        for sp in [end_month_sp, end_day_sp, end_year_sp]:
            end_date_row.add_widget(sp)

        # Show/hide repeat sub-sections based on frequency selection
        def on_freq_change(instance, value):
            is_weekly = freq_buttons["Weekly"].state == 'down'
            is_never  = freq_buttons["Never"].state == 'down'

            # Always remove all optional widgets first
            for w in [days_label, days_row, end_label, end_row, end_date_row]:
                if w.parent:
                    w.parent.remove_widget(w)

            if is_never:
                return

            # Find index just before error_label
            idx = layout.children.index(error_label)

            if is_weekly:
                layout.add_widget(end_label,   index=idx)
                layout.add_widget(end_row,     index=idx)
                layout.add_widget(days_label,  index=idx)
                layout.add_widget(days_row,    index=idx)
            else:
                # Daily / Monthly: just show repeat-end
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

        error_label = Label(text="", color=(1, 0, 0, 1),
                            size_hint_y=None, height=28)
        btn = PrimaryButton(text="Add Event", size_hint_y=None, height=44)
        layout.add_widget(error_label)
        layout.add_widget(btn)

        root.add_widget(scroll)
        popup = ThemedPopup(title="Add Event", content=root, size_hint=(0.9, 0.92))

        def on_submit(*args):
            name = name_input.text.strip()
            if not name:
                error_label.text = "Event name is required."
                return

            # "3/22"
            date_str = f"{month_sp.text}/{day_sp.text}"

            # "9:00a" / "10:00p"
            def fmt_time(h, m, ap):
                return f"{h}:{m}{'a' if ap == 'AM' else 'p'}"

            time_start = fmt_time(start_h.text, start_m.text, start_ap.text)
            time_end   = fmt_time(end_h.text,   end_m.text,   end_ap.text)

            # day_map must use mtwrfsu (r = Thursday, not th)
            day_map = {"M": "m", "T": "t", "W": "w", "Th": "r", "F": "f", "Sa": "s", "Su": "u"}

            freq = next((k for k, v in freq_buttons.items() if v.state == 'down'), "Never")
            repeat = None

            if freq != "Never":
                if freq == "Weekly":
                    selected_days = "".join(
                        day_map[d] for d in day_names if day_checks[d].active
                    )
                    rule = f"week {selected_days}" if selected_days else "week"
                elif freq == "Daily":
                    rule = "day"      # must match _str_to_time_type: "day" -> TimeType.DAY
                else:
                    rule = "month"    # must match _str_to_time_type: "month" -> TimeType.MONTH

                end_mode = next((k for k, v in end_buttons.items() if v.state == 'down'), "Forever")
                if end_mode == "Forever":
                    repeat_end = "forever"   # matches DurationType("forever")
                else:
                    repeat_end = f"until {end_month_sp.text}/{end_day_sp.text}/{end_year_sp.text}"
                    # Repeat.__init__ splits on first space -> RepeatDuration("until", "m/d/yyyy")

                repeat = Repeat(rule, repeat_end)

            notif_num_val = int(notif_num.text)
            notif_type_map = {
                "minutes": TimeType.MINUTE,
                "hours": TimeType.HOUR,
                "days": TimeType.DAY,
                "weeks": TimeType.WEEK
            }
            notif_time = NotifTime(notif_num_val, notif_type_map[notif_type.text])

            self.add_event(CalendarEvent(
                name=name,
                desc=desc_input.text.strip() or None,
                notifs=[notif_time],
                dates=DateRange(date_str),
                times=TimeRange(time_start, time_end),
                repeat=repeat
            ))
            popup.dismiss()

        btn.bind(on_release=on_submit)
        popup.open()

    def to_datetime_time(self):
        return time(self.hour, self.minute)
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.refresh(), 0.1)

class Voice(Screen): pass

class Scanner(Screen):
    def on_enter(self):
        self.ids.cam_view.ids.camera.play = True

    def on_leave(self):
        self.ids.cam_view.ids.camera.play = False

class Edit(Screen): pass

#Helps kivy manage screen_name correctly
#part of fixing the problem in root
class NavButton(Button):
    screen_name =StringProperty("")

class Root(BoxLayout):

    def on_size(self, *args):
        self.clear_widgets()

        if self.width >= 800:
            # Desktop: nav on left
            self.add_widget(self.ids.nav_bar)
            self.add_widget(self.ids.sm)
        else:
            # Mobile: nav on bottom
            self.add_widget(self.ids.sm)
            self.add_widget(self.ids.nav_bar)

    def set_active(self, screen_name):
        sm = self.ids.sm

        sm.current = screen_name

        for btn_id in ("home_button", "voice_button", "scanner_button"):
            btn = self.ids[btn_id]

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


        return Root()


if __name__ == "__main__":
    asyncio.run(WhatNow().async_run(async_lib='asyncio'))
    #WhatNow().run()
