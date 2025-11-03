import os
import queue
import subprocess

from .task import Task

class Scheduler():
    def __init__(self,
        tasks_path
    ):
        self.tasks_path = tasks_path

        self.reset()  # initialize the scheduler state

    def reset(self):
        # Load Scheduling parameters from file
        self.alg_scheduling, self.quantum, self.list_tasks = self._setup_from_file(self.tasks_path)
        self.num_tasks = len(self.list_tasks)

        # Initial simulation state
        self.time = 0                     # global simulation time
        self.used_quantum = 0             # time elapsed for the current quantum slice for FIFO/Round Robin algorithm
        self.num_term_tasks = 0           # count of completed tasks
        self.current_task = None          # the task currently running
        self.queue_tasks = queue.Queue()  # queue for FIFO/Round Robin algorithm

        self.execute()  # run the scheduler for time 0

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
        self.time += 1
        if self.current_task:
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
        # Default parameters
        default_alg_scheduling = "fifo"
        default_quantum = 2
        default_list_tasks = [Task(1,1,0,5,2),
                              Task(2,2,0,4,3),
                              Task(3,3,3,5,5),
                              Task(4,4,5,6,9),
                              Task(5,5,7,4,6)]

        # Check if file exists
        if not os.path.isfile(file_path):
            print(f'Could not find file "{file_path}". Using default scheduling parameters')
            return default_alg_scheduling, \
                   default_quantum, \
                   default_list_tasks

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Check for minimum file length
        if len(lines) < 2:
            print(f'Not enough lines in file "{file_path}". Using default scheduling parameters')
            return default_alg_scheduling, \
                   default_quantum, \
                   default_list_tasks


        # Extract parameters from file
        
        # Validate algorithm
        alg_scheduling = lines[0].split(";")[0].lower()
        if alg_scheduling not in ["fifo", "srtf", "priop"]:
            print(f'Invalid algorithm "{alg_scheduling}" in file "{file_path}". Using default {default_alg_scheduling}')
            alg_scheduling = default_alg_scheduling

        # Validate quantum
        quantum = int(lines[0].split(";")[1])
        if quantum <= 0:
            print(f'Invalid quantum "{quantum}" in file "{file_path}". Using default {default_quantum}')
            quantum = default_quantum

        # Tasks
        list_tasks = []
        for line in lines[1:]:
            task_id         = int(line.split(";")[0])
            task_color_num  = int(line.split(";")[1])
            task_start_time = int(line.split(";")[2])
            task_duration   = int(line.split(";")[3])
            task_priority   = int(line.split(";")[4])

            task = Task(task_id,
                        task_color_num,
                        task_start_time,
                        task_duration,
                        task_priority)

            list_tasks.append(task)

        return alg_scheduling, quantum, list_tasks

