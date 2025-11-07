import os
import queue
import subprocess

from .task import Task

class Scheduler():
    def __init__(self,
        app,
        tasks_path
    ):
        self.app = app
        self.tasks_path = tasks_path

    def reset(self):
        # Initial simulation state
        self.time = 0                     # global simulation time
        self.used_quantum = 0             # time elapsed for the current quantum slice for FIFO/Round Robin algorithm
        self.num_term_tasks = 0           # count of completed tasks
        self.current_task = None          # the task currently running
        self.queue_tasks = queue.Queue()  # queue for FIFO/Round Robin algorithm


        # Load Scheduling parameters from file
        self.list_tasks = []
        result = self._setup_from_file(self.tasks_path)
        if result != 0:
            # Default parameters
            self.alg_scheduling = "fifo"
            self.quantum = 2
            self.list_tasks = [
                Task(1,1,0,5,2),
                Task(2,2,0,2,3),
                Task(3,3,1,4,1),
                Task(4,4,3,1,4),
                Task(5,5,5,2,5),
            ]

        self.num_tasks = len(self.list_tasks)

        return result

    def has_tasks(self):
        # Check if there are still tasks left to run
        return True if self.num_term_tasks < len(self.list_tasks) else False

    def edit_file(self):
        # Open the tasks file with the default editor
        cmd = ["xdg-open", self.tasks_path]
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f'Error executing "{cmd}"')

    def update_current_task(self):
        if self.current_task:
            self.time += 1
            self.current_task.progress += 1
            self.current_task.turnaround_time += 1
            self.used_quantum += 1

    def update_ready_tasks(self):
        # Find all tasks that are ready
        list_tasks_ready = [t for t in self.list_tasks if t.state == "ready"]
        for task in list_tasks_ready:
            task.waiting_time += 1
            task.turnaround_time += 1

    def _exe_fifo(self):
        # FIFO/Round Robin (RR)

        # 1. Enqueue new tasks
        for task in self.list_tasks:
            if task.state == None and task.start_time <= self.time:
                task.state = "ready"
                self.queue_tasks.put(task)

        # 2. Check for preemption or task completion
        # This happens if the quantum is used up OR the current task finished
        if self.used_quantum % self.quantum == 0 or (self.current_task and self.current_task.progress == self.current_task.duration):
            if self.current_task:
                if self.current_task.progress == self.current_task.duration:
                    # Task finished
                    self.current_task.state = "terminated"
                    self.num_term_tasks += 1
                    self.used_quantum = 0
                else:
                    # Quantum expired, re-queue the task
                    self.current_task.state = "ready"
                    self.queue_tasks.put(self.current_task)
                    self.used_quantum = 0

            # 3. Get next task from the queue
            if not self.queue_tasks.empty():
                self.current_task = self.queue_tasks.get()
                self.current_task.state = "running"
            else:
                self.current_task = None
                self.used_quantum = 0  # reset quantum

    def _exe_srtf(self):
        # Shortest Remaining Time First (SRTF)

        # 1. Check if the current task finished
        if self.current_task:
            if self.current_task.progress == self.current_task.duration:
                self.current_task.state = "terminated"
                self.num_term_tasks += 1
                self.current_task = None
        
        # 2. Find the shortest ready task
        # Get all tasks that are waiting or currently running
        list_tasks_ready = [t for t in self.list_tasks if (t.state == "ready" or t.state == "running") and t.duration != t.progress]
        # Find the one with the minimum (duration - progress)
        shortest_task = min(list_tasks_ready, key=lambda t: t.duration - t.progress, default=None)

        list_tasks_new = []
        # 3. Check for newly arriving tasks
        for task in self.list_tasks:
            if task.state == None and task.start_time <= self.time:
                task.state = "ready"
                list_tasks_new.append(task)
        # Find the shortest new task (based on total duration)
        shortest_task_new = min(list_tasks_new, key=lambda t: t.duration, default=None)

        # 4. Decide whether to preempt
        if ((shortest_task_new and shortest_task and shortest_task_new.duration < shortest_task.duration - shortest_task.progress) or
            (shortest_task_new and shortest_task == None)):
            # A new task has arrived that is shorter than the remaining time of the shortest waiting task
            if self.current_task:
                self.current_task.state = "ready"  # preempt
            self.current_task = shortest_task_new
            self.current_task.state = "running"
        elif shortest_task and self.current_task == None:
            # No new tasks, just run the shortest ready task
            self.current_task = shortest_task
            self.current_task.state = "running"

    def _exe_priop(self):
        # Preemptive Priority (PRIOp)
        
        # 1. Check if the current task finished
        if self.current_task:
            if self.current_task.progress == self.current_task.duration:
                self.current_task.state = "terminated"
                self.num_term_tasks += 1
                self.current_task = None
        
        # 2. Find the highest priority ready task
        # Get all tasks that are waiting or currently running
        list_tasks_ready = [t for t in self.list_tasks if (t.state == "ready" or t.state == "running") and t.duration != t.progress]
        # Find the one with the maximum priority value
        shortest_task = max(list_tasks_ready, key=lambda t: t.priority, default=None)

        list_tasks_new = []
        # 3. Check for newly arriving tasks
        for task in self.list_tasks:
            if task.state == None and task.start_time <= self.time:
                task.state = "ready"
                list_tasks_new.append(task)
        # Find the highest priority new task
        shortest_task_new = max(list_tasks_new, key=lambda t: t.priority, default=None)

        # 4. Decide whether to preempt
        if ((shortest_task_new and shortest_task and shortest_task_new.priority > shortest_task.priority) or
            (shortest_task_new and shortest_task == None)):
            # A new task has arrived with a higher priority
            if self.current_task:
                self.current_task.state = "ready"  # Preempt
            self.current_task = shortest_task_new
            self.current_task.state = "running"
        elif shortest_task and self.current_task == None:
            # No new tasks, just run the highest priority "ready" task
            self.current_task = shortest_task
            self.current_task.state = "running"

    def execute(self):
        # Runs the scheduling logic based on the chosen algorithm.
        if self.alg_scheduling == "fifo":
            self._exe_fifo()
        elif self.alg_scheduling == "srtf":
            self._exe_srtf()
        elif self.alg_scheduling == "priop":
            self._exe_priop()

    def _setup_from_file(self, file_path):

        # Check if file exists
        if not os.path.isfile(file_path):
            return f'Could not find file "{file_path}". Using default scheduling parameters'

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Check for minimum file length
        if len(lines) < 2:
            return f'Not enough lines in file. Using default scheduling parameters'


        # Check first line size
        parts = lines[0].strip().split(";")
        parts = [p for p in parts if p != '']
        if len(parts) != 2:
            return f"Wrong number of parameters in line 1. Using default parameters"


        # Extract parameters from file
        
        # Algorithm
        alg_scheduling = lines[0].split(";")[0].lower().strip()
        if alg_scheduling in ["fifo", "srtf", "priop"]:
            self.alg_scheduling = alg_scheduling
        else:
            return f'Invalid algorithm "{alg_scheduling}" in line 1. Using default parameters'

        # Quantum
        quantum = lines[0].split(";")[1].strip()
        if quantum.isdigit() and int(quantum) != 0:
            self.quantum = int(quantum)
        else:
            return f'Invalid quantum in line 1. Using default parameters'

        # Tasks
        line_num = 2
        list_tasks = []
        for line in lines[1:]:

            # Check line size
            parts = line.strip().split(";")
            parts = [p for p in parts if p != '']
            if len(parts) < 5:
                return f"Not enough task parameters in line {line_num}. Using default parameters"

            # Task id
            task_id = parts[0].strip()
            if task_id.isdigit() and int(task_id) != 0:
                task_id = int(task_id)
            else:
                return f"Invalid task id in line {line_num}. Using default parameters"

            # Color number
            task_color_num = parts[1].strip()
            if task_color_num.isdigit():
                task_color_num = int(task_color_num)
            else:
                return f"Invalid task color number in line {line_num}. Using default parameters"

            # Start time
            task_start_time = parts[2].strip()
            if task_start_time.isdigit():
                task_start_time = int(task_start_time)
            else:
                return f"Invalid task start time in line {line_num}. Using default parameters"

            # Duration
            task_duration = parts[3].strip()
            if task_duration.isdigit() and int(task_duration) != 0:
                task_duration = int(task_duration)
            else:
                return f"Invalid task duration in line {line_num}. Using default parameters"

            # Priority
            task_priority = parts[4].strip()
            if task_priority.isdigit() and int(task_priority) != 0:
                task_priority = int(task_priority)
            else:
                return f"Invalid task priority in line {line_num}. Using default parameters"

            
            task = Task(
                task_id,
                task_color_num,
                task_start_time,
                task_duration,
                task_priority
            )
            self.list_tasks.append(task)

            line_num += 1

        return 0
