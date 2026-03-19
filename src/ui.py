from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty
from kivy.uix.filechooser import FileChooserIconView
from kivy.properties import StringProperty, ListProperty

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

class CalendarDayToday(BoxLayout):
    day_text = StringProperty("")

class EventItem(BoxLayout):
    event_type = StringProperty("")
    event_name = StringProperty("")
    event_time = StringProperty("")
