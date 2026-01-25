import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib


class Timer:
    def __init__(
        self,
        interval_ms,
        callback,
    ):
        self.interval_ms = interval_ms
        self.callback = callback
        self.timeout_id = None
        self.is_running = False

    def start(self):
        if not self.is_running:
            self.timeout_id = GLib.timeout_add(self.interval_ms, self._on_timeout)
            self.is_running = True

    def stop(self):
        if self.timeout_id and self.is_running:
            GLib.Source.remove(self.timeout_id)
            self.timeout_id = None
            self.is_running = False

    def change_interval_ms(self, new_interval_ms):
        self.interval_ms = new_interval_ms
        if self.is_running:
            self.restart()

    def restart(self):
        self.stop()
        self.start()

    def _on_timeout(self):
        self.callback()
        return True  # to keep the timeout active
