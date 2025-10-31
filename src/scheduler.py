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
        elif self.alg_scheduling == "fifo":
            self._init_fifo()
        elif self.alg_scheduling == "srtf":
            self._init_srtf()
        elif self.alg_scheduling == "priop":
            self._init_priop()

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

    def _init_fifo(self):
        for task in self.list_tasks:
            if task.start_time == 0:
                task.state = "ready"
                self.queue_tasks.put(task)

        if not self.queue_tasks.empty():
            self.current_task = self.queue_tasks.get()
            self.current_task.state = "running"

    def _init_srtf(self):
        list_ready = []
        for task in self.list_tasks:
            if task.start_time == 0:
                task.state = "ready"
                list_ready.append(task)
        shortest_task = min(list_ready, key=lambda t: t.duration)
        self.current_task = shortest_task
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

    def _fifo(self):
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

    def _srtf(self):
        if self.current_task.progress == self.current_task.duration:
            self.current_task.state = "terminated"
            self.current_task = None
        list_ready = [t for t in self.list_tasks if (t.state == "ready" or t.state == "running") and t.duration != t.progress]
        shortest_task = min(list_ready, key=lambda t: t.duration - t.progress, default=None)

        list_tasks_new = []
        # Choose the task with least duration
        for task in self.list_tasks:
            if task.state == None and task.start_time <= self.time:
                task.state = "ready"
                list_tasks_new.append(task)
        shortest_task_new = min(list_tasks_new, key=lambda t: t.duration, default=None)
        if ((shortest_task_new and shortest_task and shortest_task_new.duration < shortest_task.duration - shortest_task.progress) or 
            (shortest_task_new and shortest_task == None)):
            if self.current_task:
                self.current_task.state = "ready"
            self.current_task = shortest_task_new
            self.current_task.state = "running"
        elif shortest_task and self.current_task == None:
            self.current_task = shortest_task
            self.current_task.state = "running"                   
       
                
        
        
    def _priop(self):
        ready_tasks = [t for t in self.list_tasks if t.state != "terminated"]
        if ready_tasks:
            highest = min(ready_tasks, key=lambda t: t.priority)
            if self.current_task != highest:
                self.current_task.state = "ready"
                self.current_task = highest
                self.current_task.state = "running"

    def execute(self):
        if self.alg_scheduling == "fcfs":
            self._fcfs()
        elif self.alg_scheduling == "fifo":
            self._fifo()
        elif self.alg_scheduling == "srtf":
            self._srtf()
        elif self.alg_scheduling == "priop":
            self._priop()

    def _setup_from_file(self, file_path):
        # Default parameters
        default_alg_scheduling = "fifo"
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
        if alg_scheduling not in ["fcfs", "fifo", "srtf", "priop"]:
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
