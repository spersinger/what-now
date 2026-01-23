from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

class MyWidget(BoxLayout):
    pass

class MyApp(App):
    def build(self):
        return MyWidget()

if __name__ == '__main__':
    MyApp().run()
