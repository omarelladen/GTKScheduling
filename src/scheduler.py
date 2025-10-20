import os
import queue

from .task import Task

class Scheduler():
    def __init__(self,
        tasks_path
    ):
        self.tasks_path = tasks_path
        self.reset()

    def reset(self):
        # Scheduling parameters
        self.alg_scheduling, self.quantum, self.list_tasks = self._setup_from_file(self.tasks_path)
        self.num_tasks = len(self.list_tasks)

        self.time = 0
        self.used_quantum = 0
        self.current_task = None
        self.queue_tasks = queue.Queue()

        self.init_alg()

    def init_alg(self):
        if self.alg_scheduling == "fcfs":
            self.init_fcfs()
        elif self.alg_scheduling == "rr":
            self.init_rr()
        elif self.alg_scheduling == "sjf":
            self.init_sjf()
        elif self.alg_scheduling == "srtf":
            self.init_srtf()
        elif self.alg_scheduling == "prioc":
            self.init_prioc()
        elif self.alg_scheduling == "priop":
            self.init_priop()
        elif self.alg_scheduling == "priod":
            self.init_priod()

    def update_current_task(self):
        self.time += 1
        self.current_task.progress += 1
        self.used_quantum += 1

    def init_fcfs(self):
        for task in self.list_tasks:
            if task.start_time == 0:
                task.state = "ready"
                self.queue_tasks.put(task)

        # Get first task
        if not self.queue_tasks.empty():
            self.current_task = self.queue_tasks.get()
            self.current_task.state = "running"

    def init_rr(self):
        for task in self.list_tasks:
            if task.start_time == 0:
                task.state = "ready"
                self.queue_tasks.put(task)

        if not self.queue_tasks.empty():
            self.current_task = self.queue_tasks.get()
            self.current_task.state = "running"

    def fcfs(self):
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

    def rr(self):
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

    def sjf(self):
        if self.current_task.state == "terminated" or self.time == 0:
            # Choose the task with least duration
            ready_tasks = [t for t in self.list_tasks if t.state != "terminated"]
            if ready_tasks:
                self.current_task = min(ready_tasks, key=lambda t: t.duration)
                self.current_task.state = "running"

    def srtf(self):
        # Choose the task with least duration
        ready_tasks = [t for t in self.list_tasks if t.state != "terminated" and t.start_time <= self.time]
        if ready_tasks:
            shortest = min(ready_tasks, key=lambda t: t.duration - t.progress)
            if self.current_task != shortest:
                self.current_task.state = "ready"
                self.current_task = shortest
                self.current_task.state = "running"

    def prioc(self):
        if self.current_task.state == "terminated" or self.time == 0:
            ready_tasks = [t for t in self.list_tasks if t.state != "terminated"]
            if ready_tasks:
                self.current_task = min(ready_tasks, key=lambda t: t.priority)
                self.current_task.state = "running"

    def priop(self):
        ready_tasks = [t for t in self.list_tasks if t.state != "terminated"]
        if ready_tasks:
            highest = min(ready_tasks, key=lambda t: t.priority)
            if self.current_task != highest:
                self.current_task.state = "ready"
                self.current_task = highest
                self.current_task.state = "running"

    def priod(self):
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
            self.fcfs()
        elif self.alg_scheduling == "rr":
            self.rr()
        elif self.alg_scheduling == "sjf":
            self.sjf()
        elif self.alg_scheduling == "srtf":
            self.srtf()
        elif self.alg_scheduling == "prioc":
            self.prioc()
        elif self.alg_scheduling == "priop":
            self.priop()
        elif self.alg_scheduling == "priod":
            self.priod()

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
            return default_alg_scheduling, \
                   default_quantum, \
                   default_list_tasks

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) < 2:
            return default_alg_scheduling, \
                   default_quantum, \
                   default_list_tasks


        # Extract parameters from file
        alg_scheduling = lines[0].split(";")[0].lower()
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
