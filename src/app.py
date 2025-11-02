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
        self.scheduler = Scheduler(os.path.expanduser(TASKS_FILE))

        # Window
        self.win = Window(self,
                          self.scheduler.list_tasks,
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
        self.win.connect("destroy", self._on_destroy)
        self.win.show_all()

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
            self.win.draw_new_rect(self.scheduler.current_task)
            self.scheduler.execute()
            self.win.refresh_info_label()
        else:
            self.win.set_play_icon_on_finish()

    def skip(self):
        while self.scheduler.has_tasks():
            self.tick()
