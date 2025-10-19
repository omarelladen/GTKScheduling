import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from timer import Timer
from window import Window
from task import Task
from scheduler import Scheduler

# Include config variables
exec(open("config").read())

class App():
    def __init__(self):

        # Timer
        self.timer = Timer(300, self.tick)

        # Scheduler
        self.scheduler = Scheduler(TASKS_PATH)

        # Window
        self.win = Window(self,
                          self.scheduler.list_tasks,
                          APP_NAME,
                          APP_DESCRIPTION,
                          APP_VERSION,
                          WEBSITE_URL,
                          WEBSITE_LABEL,
                          AUTHORS,
                          COPYRIGHT,
                          APP_ICON_PATH,
                          PLAY_ICON,
                          PAUSE_ICON,
                          NEXT_ICON,
                          SKIP_ICON,
                          MENU_ICON,
                          SAVE_ICON
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
        if self.scheduler.current_task:
            self.scheduler.update_current_task()
            self.win.draw_new_rect(self.scheduler.current_task)
            self.win.refresh_info_label()
            self.scheduler.execute()
        else:
            self.win.set_stop_icon()
