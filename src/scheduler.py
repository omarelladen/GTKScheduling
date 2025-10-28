import os
import queue
import subprocess

from .task import Task

class Scheduler():
    def __init__(self,
        tasks_path
    ):
        self.tasks_path = tasks_path
        self.alg_scheduling = None
        self.quantum = None
        self.list_tasks = None
        self.num_tasks = None
        self.time = None
        self.used_quantum = None
        self.current_task = None
        self.queue_tasks = None

        self.reset()

    def reset(self):
        # Scheduling parameters
        self.alg_scheduling, self.quantum, self.list_tasks = self._setup_from_file(self.tasks_path)
        self.num_tasks = len(self.list_tasks)

        self.time = 0
        self.used_quantum = 0
        self.current_task = None
        self.queue_tasks = queue.Queue()

        self._init_alg()

    def has_tasks(self):
        return True if self.current_task else False

    def edit_file(self):
        cmd = ["xdg-open", self.tasks_path]
        result = subprocess.run(cmd)

        if result.returncode != 0:
            print(f'Error executing "{cmd}"')

    def _init_alg(self):
        if self.alg_scheduling == "fcfs":
            self._init_fcfs()
        elif self.alg_scheduling == "rr":
            self._init_rr()
        elif self.alg_scheduling == "sjf":
            self._init_sjf()
        elif self.alg_scheduling == "srtf":
            self._init_srtf()
        elif self.alg_scheduling == "prioc":
            self._init_prioc()
        elif self.alg_scheduling == "priop":
            self._init_priop()
        elif self.alg_scheduling == "priod":
            self._init_priod()

    def update_current_task(self):
        self.time += 1
        self.current_task.progress += 1
        self.used_quantum += 1

    def _init_fcfs(self):
        for task in self.list_tasks:
            if task.start_time == 0:
                task.state = "ready"
                self.queue_tasks.put(task)

        # Get first task
        if not self.queue_tasks.empty():
            self.current_task = self.queue_tasks.get()
            self.current_task.state = "running"

    def _init_rr(self):
        for task in self.list_tasks:
            if task.start_time == 0:
                task.state = "ready"
                self.queue_tasks.put(task)

        if not self.queue_tasks.empty():
            self.current_task = self.queue_tasks.get()
            self.current_task.state = "running"

    def _fcfs(self):
        # Enqueue new tasks
        for task in self.list_tasks:
            if task.state == None and task.start_time <= self.time:  #  or time +- 1
                task.state = "ready"
                self.queue_tasks.put(task)

        if self.current_task.progress == self.current_task.duration:  # current task terminated
            self.current_task.state = "terminated"

            # Get next task
            if not self.queue_tasks.empty():
                self.current_task = self.queue_tasks.get()
                self.current_task.state = "running"
            else:
                self.current_task = None

    def _rr(self):
        # Enqueue new tasks
        for task in self.list_tasks:
            if task.state == None and task.start_time <= self.time:  #  or time +- 1
                task.state = "ready"
                self.queue_tasks.put(task)

        if self.used_quantum == self.quantum or self.current_task.progress == self.current_task.duration:
            if self.current_task.progress == self.current_task.duration:
                self.current_task.state = "terminated"
                self.used_quantum = 0
            else:  # requeue
                self.current_task.state = "ready"
                self.queue_tasks.put(self.current_task)
                self.used_quantum = 0

            # Get next task
            if not self.queue_tasks.empty():
                self.current_task = self.queue_tasks.get()
                self.current_task.state = "running"
            else:
                self.current_task = None

    def _sjf(self):
        if self.current_task.state == "terminated" or self.time == 0:
            # Choose the task with least duration
            ready_tasks = [t for t in self.list_tasks if t.state != "terminated"]
            if ready_tasks:
                self.current_task = min(ready_tasks, key=lambda t: t.duration)
                self.current_task.state = "running"

    def _srtf(self):
        # Choose the task with least duration
        ready_tasks = [t for t in self.list_tasks if t.state != "terminated" and t.start_time <= self.time]
        if ready_tasks:
            shortest = min(ready_tasks, key=lambda t: t.duration - t.progress)
            if self.current_task != shortest:
                self.current_task.state = "ready"
                self.current_task = shortest
                self.current_task.state = "running"

    def _prioc(self):
        if self.current_task.state == "terminated" or self.time == 0:
            ready_tasks = [t for t in self.list_tasks if t.state != "terminated"]
            if ready_tasks:
                self.current_task = min(ready_tasks, key=lambda t: t.priority)
                self.current_task.state = "running"

    def _priop(self):
        ready_tasks = [t for t in self.list_tasks if t.state != "terminated"]
        if ready_tasks:
            highest = min(ready_tasks, key=lambda t: t.priority)
            if self.current_task != highest:
                self.current_task.state = "ready"
                self.current_task = highest
                self.current_task.state = "running"

    def _priod(self):
        # Increment priority
        for t in self.list_tasks:
            if t.state == "ready":
                t.priority = max(1, t.priority - 1)  # Considering 1 as the most important

        ready_tasks = [t for t in self.list_tasks if t.state != "terminated"]
        if ready_tasks:
            chosen = min(ready_tasks, key=lambda t: t.priority)
            if self.current_task != chosen:
                self.current_task.state = "ready"
                self.current_task = chosen
                self.current_task.state = "running"

    def execute(self):
        if self.alg_scheduling == "fcfs":
            self._fcfs()
        elif self.alg_scheduling == "rr":
            self._rr()
        elif self.alg_scheduling == "sjf":
            self._sjf()
        elif self.alg_scheduling == "srtf":
            self._srtf()
        elif self.alg_scheduling == "prioc":
            self._prioc()
        elif self.alg_scheduling == "priop":
            self._priop()
        elif self.alg_scheduling == "priod":
            self._priod()

    def _setup_from_file(self, file_path):
        # Default parameters
        default_alg_scheduling = "fcfs"
        default_quantum = 2
        default_list_tasks = [Task(1,1,0,5,2),
                              Task(2,2,0,4,3),
                              Task(3,3,3,5,5),
                              Task(4,4,5,6,9),
                              Task(5,5,7,4,6)]


        if not os.path.isfile(file_path):
            print(f'Could not find file "{file_path}". Using default scheduling parameters')
            return default_alg_scheduling, \
                   default_quantum, \
                   default_list_tasks

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) < 2:
            print(f'Not enough lines in file "{file_path}". Using default scheduling parameters')
            return default_alg_scheduling, \
                   default_quantum, \
                   default_list_tasks


        # Extract parameters from file
        alg_scheduling = lines[0].split(";")[0].lower()
        if alg_scheduling not in ["fcfs", "rr", "sjf", "srtf", "prioc", "priop", "priod"]:
            print(f'Invalid algorithm "{alg_scheduling}" in file "{file_path}". Using default scheduling parameters')
            return default_alg_scheduling, \
                   default_quantum, \
                   default_list_tasks

        quantum = int(lines[0].split(";")[1])

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
