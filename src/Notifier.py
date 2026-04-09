import asyncio
import threading
from desktop_notifier import DesktopNotifier, Icon
from pathlib import Path

class Notifier:
    def __init__(self):
        cwd = Path.cwd()
        self.icon = Icon(path=cwd.joinpath("assets", "whatnow.png"))
        self.notifier = DesktopNotifier(app_name="What Now?", app_icon=self.icon)
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self._start_loop, daemon=True).start()

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def send(self, title, message):
        # Schedule coroutine in the dedicated loop
        asyncio.run_coroutine_threadsafe(
            self.notifier.send(title=title, message=message),
            self.loop
        )
