from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.uix.filechooser import FileChooserIconView
from kivy.properties import StringProperty, ListProperty
from kivy.properties import BooleanProperty
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.spinner import Spinner
from kivy.uix.spinner import SpinnerOption
from kivy.uix.checkbox import CheckBox
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.scrollview import ScrollView

from datetime import date

from CalendarEvent import *
from Command import Command, CommandType
from globals import user_schedule, command_interpreter

class ThemedCheckBox(CheckBox):
    pass

class ThemedSpinnerOption(SpinnerOption):
    pass

class ThemedSpinner(Spinner):
    def __init__(self, **kwargs):
        kwargs.setdefault('option_cls', ThemedSpinnerOption)
        super().__init__(**kwargs)
        self.color = (0, 0, 0, 1)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)

class ThemedToggleButton(ToggleButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (1, 1, 1, 1) if self.state == 'down' else (0, 0, 0, 1)
    def on_state(self, instance, value):
        self.color = (1, 1, 1, 1) if value == 'down' else (0, 0, 0, 1)

class ThemedFileChooserIconView(FileChooserIconView):
    pass

class NavButton(Button):
    screen_name = StringProperty("")

class PrimaryButton(Button):
    pass

class ThemedPopup(Popup):
    pass

class PopupContentBox(BoxLayout):
    pass

class ThemedBox(BoxLayout):
    pass

class HeaderLabel(Label):
    pass

class VoiceTextInput(TextInput):
    pass

class CalendarDayCell(ButtonBehavior, BoxLayout):
    day_text = StringProperty("")
    day_color = ListProperty([1, 1, 1, 1])
    event_count = NumericProperty(0)
    events = ListProperty([])

    def on_event_count(self, instance, value):
        self._rebuild_bars()

    def on_kv_post(self, base_widget):
        self._rebuild_bars()

    def _rebuild_bars(self):
        bars_container = self.ids.get("event_bars")
        if bars_container is None:
            return
        bars_container.clear_widgets()

        for event in self.events:
            bar = BoxLayout(size_hint_y=None, height=15, padding=[4, 0], spacing=6)

            with bar.canvas.before:
                Color(0.878, 0.878, 0.878, 1)
                bar._rect = RoundedRectangle(pos=bar.pos, size=bar.size, radius=[2])

            bar.bind(
                pos=lambda w, v: setattr(w._rect, "pos", v),
                size=lambda w, v: setattr(w._rect, "size", v),
            )

            label = Label(
                text=event.name,
                halign="left",
                valign="middle",
                color=(0, 0, 0, 1),
                shorten=True,
                shorten_from="right",   # adds "..." at end
                font_size="11sp",
            )

            label.bind(size=label.setter("text_size"))  # ensures proper alignment

            bar.add_widget(label)
            bars_container.add_widget(bar)

    def on_press(self):
        from globals import user_schedule, command_interpreter
        from datetime import date

        print(f"Day pressed: {self.day_text}")
        root = BoxLayout(orientation='vertical', spacing=6, padding=10)
        scroll = ScrollView(size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', spacing=8, padding=[0, 0, 0, 10],
                           size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        scroll.add_widget(layout)

        today = date.today()
        date_pressed = date(today.year, today.month, int(self.day_text))
        events = user_schedule.get_for_date(date_pressed)
        root.add_widget(HeaderLabel(text=f"[b]Events for {str(date_pressed)}[/b]",
                                    size_hint_y=None, halign='left')) 
        if len(events) == 0:
            layout.add_widget(EventItem(
                event_name="No Events Today! Enjoy your day off!",
                event_time="",
                event_date=""
            ))
        else:
            for i, ev in enumerate(events):
                if i > 0:
                    layout.add_widget(Widget(size_hint_y=None, height=1))
                day, date = ev.date_range.start_date.strftime("%A"), ev.date_range.start_date
                edit_event = EditEventItem(
                    event_name=ev.name,
                    event_time=str(ev.time_range.start_time) + " - " + str(ev.time_range.end_time),
                    event_date=f"{day} - {date}"
                )
                edit_event.set_event(ev)
                layout.add_widget(edit_event)

        root.add_widget(scroll)
        popup = ThemedPopup(title="", content=root, size_hint=(0.9, 0.92))
        popup.open()

class CalendarDayToday(ButtonBehavior, BoxLayout):
    day_text = StringProperty("")
    event_count = NumericProperty(0)
    events = ListProperty([])

    def on_event_count(self, instance, value):
        self._rebuild_bars()

    def on_kv_post(self, base_widget):
        self._rebuild_bars()

    def _rebuild_bars(self):
        bars_container = self.ids.get("event_bars")
        if bars_container is None:
            return
        bars_container.clear_widgets()

        for event in self.events:
            bar = BoxLayout(size_hint_y=None, height=15, padding=[4, 0], spacing=6)

            with bar.canvas.before:
                Color(0.878, 0.878, 0.878, 1)
                bar._rect = RoundedRectangle(pos=bar.pos, size=bar.size, radius=[2])

            bar.bind(
                pos=lambda w, v: setattr(w._rect, "pos", v),
                size=lambda w, v: setattr(w._rect, "size", v),
            )

            label = Label(
                text=event.name,
                halign="left",
                valign="middle",
                color=(0, 0, 0, 1),
                shorten=True,
                shorten_from="right",   # adds "..." at end
                font_size="11sp",
            )
            label.bind(size=label.setter("text_size"))  # ensures proper alignment

            bar.add_widget(label)
            bars_container.add_widget(bar)

    def on_press(self):
        from datetime import date

        print(f"Day pressed: {self.day_text}")
        root = BoxLayout(orientation='vertical', spacing=6, padding=10)
        scroll = ScrollView(size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', spacing=8, padding=[0, 0, 0, 10],
                           size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        scroll.add_widget(layout)

        today = date.today()
        date_pressed = date(today.year, today.month, int(self.day_text))
        events = user_schedule.get_for_date(date_pressed)
        root.add_widget(HeaderLabel(text=f"[b]Events for {str(date_pressed)}[/b]",
                                    size_hint_y=None, halign='left')) 
        if len(events) == 0:
            layout.add_widget(EventItem(
                event_name="No Events Today! Enjoy your day off",
                event_time="",
                event_date=""
            ))
        else:
            for i, ev in enumerate(events):
                if i > 0:
                    layout.add_widget(Widget(size_hint_y=None, height=1))
                day, date = ev.date_range.start_date.strftime("%A"), ev.date_range.start_date
                edit_event = EditEventItem(
                    event_name=ev.name,
                    event_time=str(ev.time_range.start_time) + " - " + str(ev.time_range.end_time),
                    event_date=f"{day} - {date}"
                )
                edit_event.set_event(ev)
                layout.add_widget(edit_event)

        root.add_widget(scroll)
        popup = ThemedPopup(title="", content=root, size_hint=(0.9, 0.92))
        popup.open()



class EventItem(BoxLayout):
    event_name = StringProperty("")
    event_time = StringProperty("")
    event_date = StringProperty("")

class EditEventItem(BoxLayout):
    event_name = StringProperty("")
    event_time = StringProperty("")
    event_date = StringProperty("")
    event: CalendarEvent | None = None

    def get_home_screen(self):
        parent = self.parent
        while parent is not None:
            if type(parent).__name__ == "Home":
                return parent
            parent = parent.parent
        return None

    def set_event(self, event: CalendarEvent):
        self.event = event

    def edit_event_popup(self):
        if self.event is None:
            return

        today = date.today()
        ev = self.event

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

        # Name
        layout.add_widget(make_label("Event Name *"))
        name_input = TextInput(text=ev.name or "",
                               multiline=False, size_hint_y=None, height=40)
        layout.add_widget(name_input)

        # Description
        layout.add_widget(make_label("Description"))
        desc_input = TextInput(text=ev.description or "",
                               multiline=False, size_hint_y=None, height=40)
        layout.add_widget(desc_input)

        # Date pickers — pre-fill from event's date_range
        layout.add_widget(make_label("Start Date *"))
        months = [str(m) for m in range(1, 13)]
        days   = [str(d) for d in range(1, 32)]
        years  = [str(y) for y in range(today.year, today.year + 5)]

        start_date = ev.date_range.start_date if ev.date_range else today
        date_row = BoxLayout(orientation='horizontal', spacing=4, size_hint_y=None, height=40)
        month_sp = make_spinner_row(months, str(start_date.month))
        day_sp   = make_spinner_row(days,   str(start_date.day))
        year_sp  = make_spinner_row(years,  str(start_date.year) if str(start_date.year) in years else years[0])
        for sp in [month_sp, day_sp, year_sp]:
            date_row.add_widget(sp)
        layout.add_widget(date_row)

        # Time pickers — pre-fill from event's time_range
        hours   = [str(h) for h in range(1, 13)]
        minutes = [f"{m:02d}" for m in range(0, 60, 5)]
        ampm    = ["AM", "PM"]

        def extract_time(t):
            """Returns (hour_str, minute_str, ampm_str) from a time object."""
            h = t.hour % 12 or 12
            m = (t.minute // 5) * 5  # snap to nearest 5
            ap = "PM" if t.hour >= 12 else "AM"
            return str(h), f"{m:02d}", ap

        s_h, s_m, s_ap = extract_time(ev.time_range.start_time) if ev.time_range else ("9", "00", "AM")
        e_h, e_m, e_ap = extract_time(ev.time_range.end_time)   if ev.time_range else ("10", "00", "AM")

        layout.add_widget(make_label("Start Time *"))
        start_time_row = BoxLayout(orientation='horizontal', spacing=4, size_hint_y=None, height=40)
        start_h  = make_spinner_row(hours,   s_h)
        start_m  = make_spinner_row(minutes, s_m)
        start_ap = make_spinner_row(ampm,    s_ap)
        for sp in [start_h, start_m, start_ap]:
            start_time_row.add_widget(sp)
        layout.add_widget(start_time_row)

        layout.add_widget(make_label("End Time *"))
        end_time_row = BoxLayout(orientation='horizontal', spacing=4, size_hint_y=None, height=40)
        end_h  = make_spinner_row(hours,   e_h)
        end_m  = make_spinner_row(minutes, e_m)
        end_ap = make_spinner_row(ampm,    e_ap)
        for sp in [end_h, end_m, end_ap]:
            end_time_row.add_widget(sp)
        layout.add_widget(end_time_row)

        # Repeat frequency — pre-fill from event's repeat
        layout.add_widget(make_label("Repeat"))
        freq_row = BoxLayout(orientation='horizontal', spacing=4, size_hint_y=None, height=40)
        freq_options = ["Never", "Daily", "Weekly", "Monthly"]
        freq_buttons = {}

        current_freq = "Never"
        if ev.repeat:
            tt = ev.repeat.cycle.timespan
            if tt == TimeType.DAY:
                current_freq = "Daily"
            elif tt == TimeType.WEEK:
                current_freq = "Weekly"
            elif tt == TimeType.MONTH:
                current_freq = "Monthly"


        for opt in freq_options:
            tb = ThemedToggleButton(text=opt, group='edit_freq', size_hint=(1, None), height=40)
            if opt == current_freq:
                tb.state = 'down'
            freq_buttons[opt] = tb
            freq_row.add_widget(tb)
        layout.add_widget(freq_row)

        # Day checkboxes
        day_names  = ["M", "T", "W", "Th", "F", "Sa", "Su"]
        day_map = {"M": "m", "T": "t", "W": "w", "Th": "r", "F": "f", "Sa": "s", "Su": "u"}
        reverse_day_map = {
            Day.M: "M",  Day.T: "T",  Day.W: "W",  Day.R: "Th",
            Day.F: "F",  Day.S: "Sa", Day.U: "Su"
        }

        active_days = set()
        if ev.repeat and ev.repeat.cycle.days:
            active_days = {reverse_day_map[d] for d in ev.repeat.cycle.days if d in reverse_day_map}


        days_label = make_label("Repeat Days")
        days_row   = BoxLayout(orientation='horizontal', spacing=2, size_hint_y=None, height=40)
        day_checks = {}
        for d in day_names:
            col = BoxLayout(orientation='vertical', size_hint=(1, None), height=40)
            lbl = Label(text=d, size_hint_y=0.5)
            cb  = ThemedCheckBox(size_hint_y=0.5, active=(d in active_days))
            day_checks[d] = cb
            col.add_widget(lbl)
            col.add_widget(cb)
            days_row.add_widget(col)

        # Repeat until
        current_end = "Forever"
        end_until_date = None
        if ev.repeat and ev.repeat.duration.dur_type == DurationType.UNTIL_DATE:
            current_end = "Date"
            end_until_date = ev.repeat.duration.value  # this is a Date object

        end_label = make_label("Repeat Until")
        end_row   = BoxLayout(orientation='horizontal', spacing=4, size_hint_y=None, height=40)
        end_options = ["Forever", "Date"]
        end_buttons = {}
        for opt in end_options:
            tb = ThemedToggleButton(text=opt, group='edit_repeat_end', size_hint=(1, None), height=40)
            if opt == current_end:
                tb.state = 'down'
            end_buttons[opt] = tb
            end_row.add_widget(tb)

        end_date_row = BoxLayout(orientation='horizontal', spacing=4, size_hint_y=None, height=40)
        until = end_until_date or today
        end_month_sp = make_spinner_row(months, str(until.month))
        end_day_sp   = make_spinner_row(days,   str(until.day))
        end_year_sp  = make_spinner_row(years,  str(until.year) if str(until.year) in years else years[0])
        for sp in [end_month_sp, end_day_sp, end_year_sp]:
            end_date_row.add_widget(sp)

        error_label = Label(text="", color=(1, 0, 0, 1), size_hint_y=None, height=28)

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

        # Trigger initial show/hide state to match pre-filled values
        on_freq_change(None, None)
        if current_end == "Date":
            on_end_change(None, None)


        # Submit buttons
        submit_btn_layout = BoxLayout(orientation='horizontal', spacing=6,
                                      size_hint_y=None, height=54)
        submit_all_btn = PrimaryButton(text="Update all in series", size_hint_x=1, size_hint_y=None, height=44)
        submit_one_btn = PrimaryButton(text="Update this event only", size_hint_x=1, size_hint_y=None, height=44)
        submit_btn_layout.add_widget(submit_all_btn)
        submit_btn_layout.add_widget(submit_one_btn)
        layout.add_widget(submit_btn_layout)

        root.add_widget(scroll)
        popup = ThemedPopup(title="", content=root, size_hint=(0.9, 0.92))

        def build_updated_event():
            """Shared logic: reads form fields and returns a new CalendarEvent."""
            name = name_input.text.strip()
            if not name:
                error_label.text = "Event name is required."
                return None

            date_str  = f"{month_sp.text}/{day_sp.text}"
            def fmt_time(h, m, ap):
                return f"{h}:{m}{'a' if ap == 'AM' else 'p'}"
            time_start = fmt_time(start_h.text, start_m.text, start_ap.text)
            time_end   = fmt_time(end_h.text,   end_m.text,   end_ap.text)

            freq = next((k for k, v in freq_buttons.items() if v.state == 'down'), "Never")
            repeat = None
            if freq != "Never":
                if freq == "Weekly":
                    selected_days = "".join(day_map[d] for d in day_names if day_checks[d].active)
                    rule = f"week {selected_days}" if selected_days else "week"
                elif freq == "Daily":
                    rule = "day"
                else:
                    rule = "month"

                end_mode = next((k for k, v in end_buttons.items() if v.state == 'down'), "Forever")
                repeat_end = "forever" if end_mode == "Forever" else \
                             f"until {end_month_sp.text}/{end_day_sp.text}/{end_year_sp.text}"
                repeat = Repeat(rule, repeat_end)

            return CalendarEvent(
                name=name,
                desc=desc_input.text.strip() or None,
                notifs=ev.notif_times,
                dates=DateRange(date_str),
                times=TimeRange(time_start, time_end),
                repeat=repeat
            )

        def on_submit_one(*args):
            updated = build_updated_event()
            if updated is None:
                return

            search_event = CalendarEvent(
                name=ev.name,
                desc=None,
                notifs=[],
                dates=ev.date_range,
                times=None,
                repeat=Repeat(RepeatCycle("day", "m"), RepeatDuration("times", 0))
            )

            user_schedule.perform_command(Command(
                CommandType.EDIT,
                data=(search_event, updated)
            ))
            screen = self.get_home_screen()
            if screen:
                screen.refresh()
            popup.dismiss()

        def on_submit_all(*args):
            updated = build_updated_event()
            if updated is None:
                return

            # Search by name only — matches all events in the series
            search_event = CalendarEvent(
                name=ev.name,
                desc=None,
                notifs=[],
                dates=None,
                times=None,
                repeat=Repeat(RepeatCycle("day", "m"), RepeatDuration("times", 0))
            )

            user_schedule.perform_command(Command(
                CommandType.EDIT,
                data=(search_event, updated)
            ))
            screen = self.get_home_screen()
            if screen:
                screen.refresh()
            popup.dismiss()

        submit_one_btn.bind(on_release=on_submit_one)
        submit_all_btn.bind(on_release=on_submit_all)
        popup.open()


    def on_kv_post(self, base_widget):
        edit_btn = self.ids.edit_button
        edit_btn.bind(on_release=lambda *a: self.edit_event_popup())
