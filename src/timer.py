import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib

class Timer:
    def __init__(self,
        interval_ms,
        callback,
        *args, **kwargs,  # additional args for the callback
    ):
        self.interval_ms = interval_ms
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.timeout_id = None
        self.is_running = False

    def start(self):
        if not self.is_running:
            self.timeout_id = GLib.timeout_add(self.interval_ms, self._on_timeout)
            self.is_running = True

    def stop(self):
        if self.timeout_id is not None and self.is_running:
            GLib.Source.remove(self.timeout_id)
            self.timeout_id = None
            self.is_running = False

    def _on_timeout(self):
        """Internal callback that is called by the GLib every interval"""
        self.callback(*self.args, **self.kwargs)
        return True  # returns True to keep the timeout active
