import os

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from .task import Task
from .window import Window
from .simulator import Simulator
from .simulation_config import SimulationConfig

# Include config variables
exec(open("/usr/local/share/gtkscheduling/config").read())

class App():
    def __init__(self):

        # Metadata
        self.name = APP_NAME
        self.name_lower = APP_NAME_LOWER
        self.description = APP_DESCRIPTION
        self.version = APP_VERSION
        self.website_url = WEBSITE_URL
        self.website_label = WEBSITE_LABEL
        self.authors = AUTHORS.split(",")
        self.copyright = COPYRIGHT


        self.simulation_config = SimulationConfig(
            self,
            os.path.expanduser(TASKS_FILE)
        )

        self.simulator = Simulator(self)
        result = self.reset()
    
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

    def reset(self):
        result, alg_scheduling, quantum, list_tasks = self.simulation_config.get_params_from_file()

        if result != 0:
            # Default parameters
            alg_scheduling = "rr"
            quantum = 2
            list_tasks = [
                Task(1,1,0,5,2),
                Task(2,2,0,2,3),
                Task(3,3,1,4,1),
                Task(4,4,3,1,4),
                Task(5,5,5,2,5),
            ]

        self.simulator.reset(
            alg_scheduling,
            quantum,
            list_tasks
        )

        return result
        
    def _on_destroy(self, window):
        self.quit()

    def quit(self):
        Gtk.main_quit()

    def run(self):
        Gtk.main()
