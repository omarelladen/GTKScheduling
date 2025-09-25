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
        self.clk_duration = 300

        # Scheduler
        self.scheduler = Scheduler(TASKS_PATH)
        
        # Load GTK Window
        self.win = Window(self, self.scheduler.list_tasks, ICON_PATH)
        self.win.connect("destroy", self._on_destroy)
        self.win.show_all()
        
        # Timer
        self.timer = Timer(self.clk_duration, self.tick)
        self.timer.start()
        
    def _on_destroy(self, window):
        Gtk.main_quit()

    def run(self):
        Gtk.main()

    def tick(self):
        old_task = self.scheduler.tick()
        self.win.update_rect_time(old_task)

