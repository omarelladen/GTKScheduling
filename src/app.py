import os
import sys

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

        self.args = sys.argv[1:]  # excluding the name of the script

        # Metadata
        self.name = APP_NAME
        self.name_lower = APP_NAME_LOWER
        self.description = APP_DESCRIPTION
        self.version = APP_VERSION
        self.website_url = WEBSITE_URL
        self.website_label = WEBSITE_LABEL
        self.authors = AUTHORS.split(",")
        self.copyright = COPYRIGHT


        self.simulation_config = SimulationConfig(os.path.expanduser(TASKS_FILE))

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

    def parse_args(self):
        if "--help" in self.args or "-h" in self.args:
            self.show_help()
            sys.exit(0)
        elif "--version" in self.args or "-v" in self.args:
            self.show_version()
            sys.exit(0)

    def show_help(self):
        print("Usage:")
        print(f"  {self.name_lower} [OPTION…]")
        print("")
        print("Help Options:")
        print("  -h, --help                 Show help options")
        print("")
        print("Application Options:")
        print("  -v, --version              Print version information and exit")

    def show_version(self):
        print(f"{self.name} {self.version}")

    def reset(self):
        result, alg_scheduling, quantum, list_tasks = self.simulation_config.get_params_from_file()

        if result != 0:
            # Default parameters
            alg_scheduling = "rr"
            quantum = 2
            list_tasks = [
                Task(1,"316AD0",0,5,2),
                Task(2,"E4E32B",0,2,3),
                Task(3,"9650CB",1,4,1),
                Task(4,"4BDA3D",3,1,4),
                Task(5,"E0323C",5,2,5),
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
