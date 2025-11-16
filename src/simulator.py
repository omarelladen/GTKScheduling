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

    def has_tasks(self):
        # Check if there are still tasks left to run
        return True if self.num_term_tasks < len(self.list_tasks) else False

    def skip(self):
        while self.has_tasks():
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

        self.scheduler.current_task = None

    def update_current_task(self):
        if self.scheduler.current_task:
            self.time += 1
            self.scheduler.current_task.progress += 1
            self.scheduler.current_task.turnaround_time += 1
            self.used_quantum += 1

    def update_ready_tasks(self):
        list_tasks_ready = [t for t in self.list_tasks if t.state == "ready"]
        for task in list_tasks_ready:
            task.waiting_time += 1
            task.turnaround_time += 1

    def execute_scheduler(self):
        if self.alg_scheduling == "rr":
            self.scheduler.monitor_rr()
            if self.scheduler.interrupt:
                self.scheduler.exe_rr()
        elif self.alg_scheduling == "srtf":
            self.scheduler.monitor_srtf()
            if self.scheduler.interrupt:
                self.scheduler.exe_srtf()
        elif self.alg_scheduling == "priop":
            self.scheduler.monitor_priop()
            if self.scheduler.interrupt:
                self.scheduler.exe_priop()

        self.scheduler.interrupt = False

    def tick(self):
        if self.has_tasks():
            self.execute_scheduler()
            self.update_current_task()
            self.update_ready_tasks()
            self.app.window.draw_new_rect(self.scheduler.current_task)
            self.app.window.refresh_info_label()
        else:
            self.app.window.set_play_icon_on_finish()
