import os
import re
import importlib
import subprocess

from .task import Task

class SimulationConfig():
    def __init__(self,
        tasks_path,
        alg_dir_path
    ):
        self.tasks_path = tasks_path
        self.alg_dir_path = alg_dir_path

    def edit_file(self):
        # Open the tasks file with the default editor
        cmd = ["xdg-open", self.tasks_path]
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f'Error executing "{cmd}"')

    def find_algorithms(self):
        list_scheduler = []
        list_monitor = []
        for filename in os.listdir(self.alg_dir_path):
            if os.path.isfile(os.path.join(self.alg_dir_path, filename)):
                if filename.startswith("scheduler_") and filename.endswith(".py"):
                    alg_name = filename[len("scheduler_"):-len(".py")]
                    list_scheduler.append(alg_name)

                elif filename.startswith("monitor_") and filename.endswith(".py"):
                    alg_name = filename[len("monitor_"):-len(".py")]
                    list_monitor.append(alg_name)

        return [alg for alg in list_scheduler if alg in list_monitor]

    def import_monitor(self, alg):
        try:
            module_name = f"{__package__}.monitor_{alg}"
            class_name = "Monitor"
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            return cls
        except (ModuleNotFoundError, AttributeError) as e:
            print(f'Error importing class "{class_name}" from module "{module_name}": {e}')
            return None

    def import_scheduler(self, alg):
        try:
            module_name = f"{__package__}.scheduler_{alg}"
            class_name = "Scheduler"
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            return cls
        except (ModuleNotFoundError, AttributeError) as e:
            print(f'Error importing class "{class_name}" from module "{module_name}": {e}')
            return None

    def import_task(self, alg):
        try:
            module_name = f"{__package__}.task_{alg}"
            class_name = "Task"
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            return cls
        except (ModuleNotFoundError, AttributeError) as e:
            return Task

    def get_params_from_file(self):

        # Check if file exists
        if not os.path.isfile(self.tasks_path):
            return f'Could not find file "{self.tasks_path}". Using default scheduling parameters', None, None, None, None

        with open(self.tasks_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Check for minimum file length
        if len(lines) < 2:
            return f'Not enough lines in file. Using default scheduling parameters', None, None, None, None


        line_num = 1

        # Check first line size
        parts = lines[0].strip().split(";")
        parts = [p for p in parts if p != ""]
        if len(parts) != 3:
            return f"Wrong number of parameters in line {line_num}. Using default parameters", None, None, None, None


        # Extract parameters from file
        
        # Algorithm
        alg_scheduling = lines[0].split(";")[0].lower().strip()
        list_alg = self.find_algorithms()
        if not alg_scheduling in list_alg:
            return f'Invalid algorithm "{alg_scheduling}" in line {line_num}. Options are {list_alg}. Using default parameters', None, None, None, None

        # Quantum
        quantum = lines[0].split(";")[1].strip()
        if quantum.isdigit() and int(quantum) != 0:
            quantum = int(quantum)
        else:
            return f"Invalid quantum in line {line_num}. Using default parameters", None, None, None, None

        # Alpha
        alpha = lines[0].split(";")[2].strip()
        if alpha.isdigit() and int(alpha) != 0:
            alpha = int(alpha)
        else:
            return f"Invalid alpha in line {line_num}. Using default parameters", None, None, None, None


        line_num += 1

        # Tasks
        list_tasks = []
        for line in lines[1:]:

            # Check line size
            parts = line.strip().split(";")
            parts = [p for p in parts if p != ""]  # ignore empty fields
            if len(parts) < 5:
                return f"Not enough task parameters in line {line_num}. Using default parameters", None, None, None, None

            # Task id
            task_id = parts[0].replace("t", "").strip()
            if task_id.isdigit() and int(task_id) != 0:
                task_id = int(task_id)
            else:
                return f"Invalid task id in line {line_num}. Using default parameters", None, None, None, None

            # Color code
            task_color_hex = parts[1].strip().lstrip("#").lower()
            if not re.fullmatch(r"[0-9a-f]{6}", task_color_hex):
                return f"Invalid task color code in line {line_num}. Using default parameters", None, None, None, None

            # Start time
            task_start_time = parts[2].strip()
            if task_start_time.isdigit():
                task_start_time = int(task_start_time)
            else:
                return f"Invalid task start time in line {line_num}. Using default parameters", None, None, None, None

            # Duration
            task_duration = parts[3].strip()
            if task_duration.isdigit() and int(task_duration) != 0:
                task_duration = int(task_duration)
            else:
                return f"Invalid task duration in line {line_num}. Using default parameters", None, None, None, None

            # Priority
            task_priority = parts[4].strip()
            if task_priority.isdigit() and int(task_priority) != 0:
                task_priority = int(task_priority)
            else:
                return f"Invalid task priority in line {line_num}. Using default parameters", None, None, None, None


            # Events
            list_task_events = []
            if len(parts) > 5:
                for i in range(5, len(parts)):
                    event = parts[i].lower().strip()

                    valid_event = False

                    # I/O
                    re_match = re.match(r"io:(\d+)-(\d+)", event)
                    if re_match:
                        io_time     = int(re_match.group(1))
                        io_duration = int(re_match.group(2))
                        if io_duration == 0:
                            return f"Invalid task event duration '0' in line {line_num}. Using default parameters", None, None, None, None
                        list_task_events.append(("io", io_time, io_duration))
                        valid_event = True

                    # Mutex Lock
                    re_match = re.match(r"ml(\d+):(\d+)", event)
                    if re_match:
                        ml_id   = int(re_match.group(1))
                        ml_time = int(re_match.group(2))
                        list_task_events.append(("ml", ml_id, ml_time))
                        valid_event = True

                    # Mutex Unlock
                    re_match = re.match(r"mu(\d+):(\d+)", event)
                    if re_match:
                        mu_id   = int(re_match.group(1))
                        mu_time = int(re_match.group(2))
                        list_task_events.append(("mu", mu_id, mu_time))
                        valid_event = True
                    
                    if not valid_event:
                        return f"Invalid task event in line {line_num}. Using default parameters", None, None, None, None


            class_task = self.import_task(alg_scheduling)
            task = class_task(
                task_id,
                task_color_hex,
                task_start_time,
                task_duration,
                task_priority,
                list_task_events
            )
            list_tasks.append(task)

            line_num += 1

        return 0, alg_scheduling, quantum, alpha, list_tasks
