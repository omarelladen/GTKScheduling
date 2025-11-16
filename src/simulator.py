import queue

from .timer import Timer
from .scheduler import Scheduler

class Simulator():
    def __init__(self,
        app
    ):
        self.app = app

        # Timer
        self.timer = Timer(
            interval_ms=300,
            callback=self.tick
        )

        # Scheduler
        self.scheduler = Scheduler(self)

    def finished(self):
        # Check if there are still tasks left to run
        return False if self.num_term_tasks < len(self.list_tasks) else True

    def skip(self):
        while not self.finished():
            self.tick()

    def reset(self, alg_scheduling, quantum, list_tasks):
        self.alg_scheduling = alg_scheduling
        self.quantum = quantum
        self.list_tasks = list_tasks

        # Initial simulation state
        self.time = 0                     # global simulation time
        self.used_quantum = 0             # time elapsed for the current quantum slice for Round Robin algorithm
        self.num_term_tasks = 0           # count of completed tasks
        self.queue_tasks = queue.Queue()  # queue for Round Robin algorithm

        self.num_tasks = len(self.list_tasks)

        self.current_task = None

    def update_ready_tasks(self):
        list_tasks_ready = [t for t in self.list_tasks if t.state == "ready"]
        for task in list_tasks_ready:
            task.waiting_time += 1
            task.turnaround_time += 1

    def execute_monitor(self):
        if self.alg_scheduling == "rr":
            return self.scheduler.monitor_rr()
        elif self.alg_scheduling == "srtf":
            return self.scheduler.monitor_srtf()
        elif self.alg_scheduling == "priop":
            return self.scheduler.monitor_priop()

    def execute_scheduler(self):
        if self.alg_scheduling == "rr":
            self.scheduler.exe_rr()
        elif self.alg_scheduling == "srtf":
            self.scheduler.exe_srtf()
        elif self.alg_scheduling == "priop":
            self.scheduler.exe_priop()

    def tick(self):
        if not self.finished():

            # Monitor tasks
            interrupt = self.execute_monitor()

            # Call scheduler if needed
            if interrupt:
                self.execute_scheduler()
            if self.current_task:
                self.current_task.execute()
                self.time += 1
                self.used_quantum += 1

            self.update_ready_tasks()

            self.app.window.draw_new_rect(self.current_task)
            self.app.window.refresh_info_label()
        else:
            self.app.window.set_play_icon_on_finish()

    def terminate_task(self, task):
        task.state = "terminated"
        self.num_term_tasks += 1
        self.used_quantum = 0
        self.current_task = None

    def preempt_task(self, task):
        self.current_task.state = "ready"
        self.used_quantum = 0

    def load_new_task(self, task):
        task.state = "ready"

    def schedule_task(self, task):
        self.current_task = task
        task.state = "running"
     
    def suspend_task(self, task):
        pass
