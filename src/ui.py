from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty

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
