import queue

from .timer import Timer
from .mutex import Mutex


class Simulator():
    def __init__(
        self,
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

        self.list_mutexes = []

        self.deadlock = False

    def tick(self):
        if self.app.window.list_task_rects_back:
            self.app.window.advance()

        elif not self.finished():

            self.check_io_finish()

            # Monitor tasks
            self.interrupt = self.monitor.execute()

            # Call scheduler if needed
            if self.interrupt or self.event_interrupt:
                self._schedule()

            self.update_ready_tasks()
            self.update_suspended_tasks()

            # Execute scheduled task
            if self.current_task:
                self.current_task.execute(self)

            while self.event_interrupt:
                self.monitor.execute()
                self._schedule()
                if self.current_task:
                    self.current_task.execute(self)


            self.time += 1

            for task in self.list_tasks:
                if task.state in ["ready", "suspended", "running"]:
                    task.turnaround_time += 1

            self.app.window.draw_new_rect(self.current_task)
            self.app.window.refresh_info_label()

            if self.detect_deadlock():
                print("deadlock")
                self.deadlock = True
                self.app.window.open_error_dialog("deadlock")
                self.app.simulator.timer.stop()
                self.app.window.set_play_icon_on_finish()

        else:
            self.app.window.set_play_icon_on_finish()

    def _schedule(self):
        self.scheduler.execute()
        print("scheduler call")
        if self.current_task:
            print("schedule", self.current_task.id)
        self.update_ready_tasks_when_scheduling()
        self.event_interrupt = False
        self.interrupt = False

    def update_ready_tasks(self):
        list_tasks_ready = [t for t in self.list_tasks if t.state == "ready"]
        for task in list_tasks_ready:
            task.update_ready()

    def update_suspended_tasks(self):
        list_tasks_suspended = [t for t in self.list_tasks if t.state == "suspended"]
        for task in list_tasks_suspended:
            task.update_suspended()

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

    def io_req(self):
        self.suspend_task()
        self.event_interrupt = True

    def suspend_task(self):
        self.current_task.suspend()
        self.used_quantum = 0
        self.current_task = None

    def unsuspend_task(self, task):
        task.unsuspend()
        self.event_interrupt = True

    def ml_req(self, mutex_id):
        if not any(mutex.id == mutex_id for mutex in self.list_mutexes):
            print("Create Mutex", mutex_id)
            mutex = Mutex(mutex_id, self)
            self.list_mutexes.append(mutex)

        mutex = next((m for m in self.list_mutexes if m.id == mutex_id))
        mutex.lock(self.current_task)

        self.event_interrupt = True

    def detect_deadlock(self):
        for mutex_1 in self.list_mutexes:
            owner_1 = mutex_1.owner
            if owner_1:
                for mutex_2 in self.list_mutexes:
                    if mutex_2 != mutex_1:
                        owner_2 = mutex_2.owner
                        if owner_2:
                            if owner_1 in mutex_2.queue_tasks.queue and owner_2 in mutex_1.queue_tasks.queue:
                                return True
        return False

    def mu_req(self, mutex_id):
        mutex = next((m for m in self.list_mutexes if m.id == mutex_id))
        mutex.unlock(self.current_task)

        self.event_interrupt = True

    def check_io_finish(self):
        self.event_interrupt = False
        list_tasks_suspended = [t for t in self.list_tasks if t.state == "suspended"]
        for task in list_tasks_suspended:
            for event in task.list_ongoing_io.copy():  # copy bc events can be removed inside the loop
                if event[0] == "io" and event[2] == task.io_progress:
                    print("io finish")
                    self.unsuspend_task(task)
                    task.io_progress = 0
                    task.list_ongoing_io.remove(event)
