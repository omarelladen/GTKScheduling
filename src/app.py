import os

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from .timer import Timer
from .window import Window
from .scheduler import Scheduler

# Include config variables
exec(open("/usr/local/share/gtkscheduling/config").read())

class App():
    def __init__(self):
        self.name = APP_NAME
        self.name_lower = APP_NAME_LOWER
        self.description = APP_DESCRIPTION
        self.version = APP_VERSION
        self.website_url = WEBSITE_URL
        self.website_label = WEBSITE_LABEL
        self.authors = AUTHORS.split(",")
        self.copyright = COPYRIGHT

        # Timer
        self.timer = Timer(interval_ms=300, callback=self.tick)

        # Scheduler
        self.scheduler = Scheduler(self, os.path.expanduser(TASKS_FILE))
        result = self.scheduler.reset()

        # Window
        self.window = Window(
            self,
            APP_ICON_FILE,
            PLAY_ICON,
            PAUSE_ICON,
            NEXT_ICON,
            SKIP_ICON,
            RESTART_ICON,
            MENU_ICON,
            SAVE_ICON,
            EDIT_ICON
        )
        self.window.connect("destroy", self._on_destroy)
        self.window.show_all()

        if result != 0:
            self.window.open_error_dialog(result)


    def _on_destroy(self, window):
        self.quit()

    def quit(self):
        Gtk.main_quit()

    def run(self):
        Gtk.main()

    def tick(self):
        if self.scheduler.has_tasks():
            self.scheduler.update_current_task()
            self.scheduler.update_ready_tasks()
            self.window.draw_new_rect(self.scheduler.current_task)
            self.scheduler.execute()
            self.window.refresh_info_label()
        else:
            self.window.set_play_icon_on_finish()

    def skip(self):
        while self.scheduler.has_tasks():
            self.tick()
