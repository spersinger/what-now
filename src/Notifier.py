import asyncio
import sys
from desktop_notifier import DesktopNotifier, Icon
from pathlib import Path
from kivy.clock import Clock

class Notifier:
    def __init__(self):
        cwd = Path.cwd()
        self.icon = Icon(path=cwd.joinpath("assets", "whatnow.png"))
        self.notifier = DesktopNotifier(app_name="What Now?", app_icon=self.icon)

    def send(self, title, message):
        # Schedule on Kivy's main thread, safe for WinRT on Windows
        Clock.schedule_once(lambda dt: self._send(title, message), 0.1)

    def _send(self, title, message):
        asyncio.ensure_future(
            self.notifier.send(title=title, message=message)
        )
