import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


from timer import Timer
from window import Window

# Include config variables
exec(open('config').read())

class App():
    def __init__(self):
        
        # Scheduling parameters
        self.time = 0
        self.quantum = 2
        self.current_task = 1
        self.num_tasks = 5
        self.clk_duration = 200
       
        # Load GTK Window
        self.win = Window(ICON_FILE, BAR_SIZES_FILE, self)
        self.win.connect("destroy", self._on_destroy)
        self.win.show_all()
        
        # Timer
        self.timer = Timer(self.clk_duration, self.tick)
        self.timer.start()  # Inicia o timer
        
    def _on_destroy(self, window):
        Gtk.main_quit()

    def tick(self):
        self.time+=1;
        print(f"Tick {self.time}", end='')
        self.win.update_rect_time(self.current_task)
        if self.time % self.quantum == 0:
            print(f" - Change to task {self.current_task}", end='')
            if self.current_task == self.num_tasks:
                self.current_task = 1
            else:
                self.current_task += 1
        print("\n", end='')
        
    def run(self):
        Gtk.main()
