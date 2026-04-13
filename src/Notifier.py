import sys
from pathlib import Path
from kivy.clock import Clock


# pyjnius stuff for android notifications api
from pyjnius import autoclass

class Notifier:
    def __init__(self):
        cwd = Path.cwd()
        # self.icon = Icon(path=cwd.joinpath("assets", "whatnow.png"))
        # self.notifier = DesktopNotifier(app_name="What Now?", app_icon=self.icon)

    def send(self, title, message):
        # could use plyer notification for this; pyjnius used for delayed notification
        # (ex. for when app is closed)
        pass
        
    # schedule a notification with the offset
    def schedule_notif(self, title, message, delay):
        pass
