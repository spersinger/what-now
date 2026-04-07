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
            )
            label.bind(size=label.setter("text_size"))  # ensures proper alignment

            bar.add_widget(label)
            bars_container.add_widget(bar)

    def on_press(self):
        from globals import user_schedule, command_interpreter

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
                event_type='No Events Today! Enjoy your day off!',
                event_name="",
                event_time="",
                event_date=""
            ))
        else:
            for i, ev in enumerate(events):
                if i > 0:
                    layout.add_widget(Widget(size_hint_y=None, height=1))
                layout.add_widget(EditEventItem(
                    event_type='Lecture',
                    event_name=ev.name,
                    event_time=str(ev.time_range.start_time) + " - " + str(ev.time_range.end_time),
                    event_date=""
                ))

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
            )
            label.bind(size=label.setter("text_size"))  # ensures proper alignment

            bar.add_widget(label)
            bars_container.add_widget(bar)

    def on_press(self):
        from globals import user_schedule, command_interpreter

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
                event_type='No Events Today! Enjoy your day off!',
                event_name="",
                event_time="",
                event_date=""
            ))
        else:
            for i, ev in enumerate(events):
                if i > 0:
                    layout.add_widget(Widget(size_hint_y=None, height=1))
                layout.add_widget(EditEventItem(
                    event_type='Lecture',
                    event_name=ev.name,
                    event_time=str(ev.time_range.start_time) + " - " + str(ev.time_range.end_time),
                    event_date=""
                ))

        root.add_widget(scroll)
        popup = ThemedPopup(title="", content=root, size_hint=(0.9, 0.92))
        popup.open()



class EventItem(BoxLayout):
    event_type = StringProperty("")
    event_name = StringProperty("")
    event_time = StringProperty("")
    event_date = StringProperty("")

class EditEventItem(BoxLayout):
    event_type = StringProperty("")
    event_name = StringProperty("")
    event_time = StringProperty("")
    event_date = StringProperty("")

    def edit_event(self):
        from globals import user_schedule, command_interpreter

        #search_event = CalendarEvent(
                #name = self.event_name,
                #desc = None,
                #dates = DateRange(self.event_date, self.event_date),
                #times = None,
                #repeat = None
                #)
        #print(search_event)
