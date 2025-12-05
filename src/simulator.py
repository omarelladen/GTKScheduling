import queue

from .timer import Timer

class Simulator():
    def __init__(self,
        app,
        simulation_config
    ):
        self.app = app
        self.simulation_config = simulation_config

        # Timer
        self.timer = Timer(
            interval_ms=300,
            callback=self.tick
        )

    def finished(self):
        # Check if there are still tasks left to run
        return False if self.num_term_tasks < len(self.list_tasks) else True

    def skip(self):
        while not self.finished():
            self.tick()

    def reset(self, alg_scheduling, quantum, alpha, list_tasks):
        self.alg_scheduling = alg_scheduling
        self.quantum = quantum
        self.alpha = alpha
        self.list_tasks = list_tasks

        # Scheduler
        class_scheduler = self.simulation_config.import_scheduler(alg_scheduling)
        if class_scheduler:
            self.scheduler = class_scheduler(self)

        # Monitor
        class_monitor = self.simulation_config.import_monitor(alg_scheduling)
        if class_monitor:
            self.monitor = class_monitor(self)

        # Initial simulation state
        self.time = 0                     # global simulation time
        self.used_quantum = 0             # time elapsed for the current quantum slice for Round Robin algorithm
        self.num_term_tasks = 0           # count of completed tasks
        self.queue_tasks = queue.Queue()  # queue for Round Robin algorithm

        self.num_tasks = len(self.list_tasks)

        self.current_task = None

        self.list_tasks_new = []
        self.list_tasks_previous = []

    def tick(self):
        if not self.finished():

            # Monitor tasks
            interrupt = self.monitor.execute()

            # Call scheduler if needed
            if interrupt:
                self.scheduler.execute()
                self.update_ready_tasks_when_scheduling()

            self.update_ready_tasks()
                
            if self.current_task:
                self.current_task.execute()
                self.time += 1
                self.used_quantum += 1

            self.app.window.draw_new_rect(self.current_task)
            self.app.window.refresh_info_label()
        else:
            self.app.window.set_play_icon_on_finish()

    def update_ready_tasks(self):
        list_tasks_ready = [t for t in self.list_tasks if t.state == "ready"]
        for task in list_tasks_ready:
            task.update_ready()

    def update_ready_tasks_when_scheduling(self):
        list_tasks_ready = [t for t in self.list_tasks if t.state == "ready"]
        for task in list_tasks_ready:
            task.update_ready_when_scheduling(self.alpha)

    def terminate_task(self, task):
        task.terminate()
        self.num_term_tasks += 1
        self.used_quantum = 0
        self.current_task = None

    def preempt_task(self, task):
        task.preempt()
        self.used_quantum = 0

    def load_task(self, task):
        task.load()

    def schedule_task(self, task):
        self.current_task = task
        task.schedule()
     
    def suspend_task(self, task):
        pass
