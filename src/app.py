import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from timer import Timer
from window import Window
from task import Task
from scheduler import Scheduler

# Include config variables
exec(open('config').read())

class App():
    def __init__(self):

        # Timer
        self.timer = Timer(300, self.tick)
        
        # Scheduler
        self.scheduler = Scheduler(TASKS_PATH)
        
        # Window
        self.win = Window(self, self.scheduler.list_tasks, ICON_PATH)
        self.win.connect("destroy", self._on_destroy)
        self.win.show_all()
        
    def _on_destroy(self, window):
        Gtk.main_quit()

    def run(self):
        Gtk.main()

    def tick(self):
        self.scheduler.update_current_task()
        self.win.update_rect_time(self.scheduler.current_task)
        self.scheduler.execute()
