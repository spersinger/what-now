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
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.config import Config
from kivy.clock  import Clock

import calendar
import datetime

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
from Voice import Voice
from document_scanner import DocumentScanner
from ui import *
from globals import user_schedule, command_interpreter

import calendar

# TODO: Move to seperate file
class Home(Screen):
    def add_event(self, event: CalendarEvent):
        user_schedule.add_event(event)
        self.refresh()

    def refresh(self):
        today = datetime.date.today()
        self.build_calendar(today.year, today.month)
        self.build_events(user_schedule.get_for_date(datetime.date.today()))

    def build_calendar(self, year, month):
        grid = self.ids.calendar_grid
        grid.clear_widgets()
        today = datetime.date.today().day
        first_weekday = calendar.monthrange(year, month)[0]
        start_offset = (first_weekday + 1) % 7
        for _ in range(start_offset):
            grid.add_widget(Widget(size_hint_y=None, height=30))

        event_counts = user_schedule.get_event_counts(year, month)  # dict: {day: count}

        for day in range(1, calendar.monthrange(year, month)[1] + 1):
            count = event_counts.get(day, 0)
            if day == today:
                cell = CalendarDayToday(day_text=str(day), event_count=count)
            else:
                color = [0.333, 0.333, 0.333, 1] if ... else [1, 1, 1, 1]
                cell = CalendarDayCell(day_text=str(day), day_color=color, event_count=count)
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
                box.add_widget(EditEventItem(
                    event_type='Lecture',
                    event_name=ev.name,
                    event_time=str(ev.time_range.start_time) + " - " + str(ev.time_range.end_time),
                    event_date=""
                ))

    def on_kv_post(self, base_widget):
        # Preseeded, just for now though
        self.add_event(CalendarEvent(
            name="Intro to Computing",
            desc="Intro to Computing class",
            notifs=[NotifTime(15)],
            dates=DateRange("4/1"),
            times=TimeRange("9:00a", "10:00a"),
            repeat=Repeat("week mwf", "forever")
        ))
        self.add_event(CalendarEvent(
            name="Language Translation",
            desc="Language Translation class",
            notifs=[NotifTime(15)],
            dates=DateRange("4/2"),
            times=TimeRange("12:30p", "1:45p"),
            repeat=Repeat("week tr", "forever")
        ))

        search_event_btn = self.ids.search_event_button
        search_event_btn.bind(on_release=lambda *a: self.search_event_popup())
        add_event_btn = self.ids.add_event_button
        add_event_btn.bind(on_release=lambda *a: self.add_event_popup())

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
                event_type='No events found!',
                event_name="",
                event_time="",
                event_date=""
            ))
        else:
            ev, g_idx, e_idx = result  # unpack the tuple
            layout.add_widget(EditEventItem(
                event_type='Lecture',
                event_name=ev.name,
                event_time=str(ev.time_range.start_time) + " - " + str(ev.time_range.end_time),
                event_date=""
            ))

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

            self.add_event(CalendarEvent(
                name=name,
                desc=desc_input.text.strip() or None,
                notifs=[NotifTime(15)],
                dates=DateRange(date_str),
                times=TimeRange(time_start, time_end),
                repeat=repeat
            ))
            popup.dismiss()
        
        btn.bind(on_release=on_submit)
        popup.open()

class Voice(Screen): pass

class Scanner(Screen):
    def on_enter(self):
        self.ids.cam_view.ids.camera.play = True

    def on_leave(self):
        self.ids.cam_view.ids.camera.play = False

class Edit(Screen): pass
class Root(BoxLayout):
    def set_active(self, screen_name):
        sm = self.ids.sm
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
