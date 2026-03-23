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

class CalendarDayCell(BoxLayout):
    day_text = StringProperty("")
    day_color = ListProperty([1, 1, 1, 1])
    event_count = NumericProperty(0)

    def on_event_count(self, instance, value):
        self._rebuild_bars()

    def on_kv_post(self, base_widget):
        self._rebuild_bars()

    def _rebuild_bars(self):
        bars_container = self.ids.get("event_bars")
        if bars_container is None:
            return
        bars_container.clear_widgets()
        for _ in range(self.event_count):
            bar = Widget(size_hint_y=None, height=4)
            with bar.canvas:
                Color(0.878, 0.878, 0.878, 1)
                bar._rect = RoundedRectangle(pos=bar.pos, size=bar.size, radius=[2])
            bar.bind(
                pos=lambda w, v: setattr(w._rect, "pos", v),
                size=lambda w, v: setattr(w._rect, "size", v),
            )
            bars_container.add_widget(bar)

class CalendarDayToday(BoxLayout):
    day_text = StringProperty("")
    event_count = NumericProperty(0)

    def on_event_count(self, instance, value):
        self._rebuild_bars()

    def on_kv_post(self, base_widget):
        self._rebuild_bars()

    def _rebuild_bars(self):
        bars_container = self.ids.get("event_bars")
        if bars_container is None:
            return
        bars_container.clear_widgets()
        for _ in range(self.event_count):
            bar = Widget(size_hint_y=None, height=4)
            with bar.canvas:
                Color(0.878, 0.878, 0.878, 1)
                bar._rect = RoundedRectangle(pos=bar.pos, size=bar.size, radius=[2])
            bar.bind(
                pos=lambda w, v: setattr(w._rect, "pos", v),
                size=lambda w, v: setattr(w._rect, "size", v),
            )
            bars_container.add_widget(bar)



class EventItem(BoxLayout):
    event_type = StringProperty("")
    event_name = StringProperty("")
    event_time = StringProperty("")
    event_date = StringProperty("")
