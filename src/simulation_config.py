import os
import subprocess

from .task import Task

class SimulationConfig():
    def __init__(self,
        tasks_path
    ):
        self.tasks_path = tasks_path

    def edit_file(self):
        # Open the tasks file with the default editor
        cmd = ["xdg-open", self.tasks_path]
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f'Error executing "{cmd}"')

    def get_params_from_file(self):

        # Check if file exists
        if not os.path.isfile(self.tasks_path):
            return f'Could not find file "{self.tasks_path}". Using default scheduling parameters', None, None, None

        with open(self.tasks_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Check for minimum file length
        if len(lines) < 2:
            return f'Not enough lines in file. Using default scheduling parameters', None, None, None


        # Check first line size
        parts = lines[0].strip().split(";")
        parts = [p for p in parts if p != '']
        if len(parts) != 2:
            return f"Wrong number of parameters in line 1. Using default parameters", None, None, None


        # Extract parameters from file
        
        # Algorithm
        alg_scheduling = lines[0].split(";")[0].lower().strip()
        if not alg_scheduling in ["rr", "srtf", "priop"]:
            return f'Invalid algorithm "{alg_scheduling}" in line 1. Using default parameters', None, None, None

        # Quantum
        quantum = lines[0].split(";")[1].strip()
        if quantum.isdigit() and int(quantum) != 0:
            quantum = int(quantum)
        else:
            return f'Invalid quantum in line 1. Using default parameters', None, None, None

        # Tasks
        line_num = 2
        list_tasks = []
        for line in lines[1:]:

            # Check line size
            parts = line.strip().split(";")
            parts = [p for p in parts if p != '']
            if len(parts) < 5:
                return f"Not enough task parameters in line {line_num}. Using default parameters", None, None, None

            # Task id
            task_id = parts[0].strip()
            if task_id.isdigit() and int(task_id) != 0:
                task_id = int(task_id)
            else:
                return f"Invalid task id in line {line_num}. Using default parameters", None, None, None

            # Color number
            task_color_num = parts[1].strip()
            if task_color_num.isdigit():
                task_color_num = int(task_color_num)
            else:
                return f"Invalid task color number in line {line_num}. Using default parameters", None, None, None

            # Start time
            task_start_time = parts[2].strip()
            if task_start_time.isdigit():
                task_start_time = int(task_start_time)
            else:
                return f"Invalid task start time in line {line_num}. Using default parameters", None, None, None

            # Duration
            task_duration = parts[3].strip()
            if task_duration.isdigit() and int(task_duration) != 0:
                task_duration = int(task_duration)
            else:
                return f"Invalid task duration in line {line_num}. Using default parameters", None, None, None

            # Priority
            task_priority = parts[4].strip()
            if task_priority.isdigit() and int(task_priority) != 0:
                task_priority = int(task_priority)
            else:
                return f"Invalid task priority in line {line_num}. Using default parameters", None, None, None

            
            task = Task(
                task_id,
                task_color_num,
                task_start_time,
                task_duration,
                task_priority
            )
            list_tasks.append(task)

            line_num += 1

        return 0, alg_scheduling, quantum, list_tasks
