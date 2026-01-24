import queue

class Mutex():
    def __init__(
        self,
        id,
        simulator
    ):
        self.id = id
        self.simulator = simulator
        self.owner = None
        self.queue_tasks = queue.Queue()

    def lock(self, task):
        if self.owner:
            self.queue_tasks.put(task)
            self.simulator.suspend_task()
        else:
            self.owner = task

    def unlock(self, task):
        if task == self.owner:
            if not self.queue_tasks.empty():
                task_to_awake = self.queue_tasks.get()
                self.owner = task_to_awake
                self.simulator.unsuspend_task(task_to_awake)
            else:
                self.owner = None
