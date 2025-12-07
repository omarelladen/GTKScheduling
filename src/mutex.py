import queue

class Mutex():
    def __init__(self,
        id,
        simulator
    ):
        self.id = id
        self.simulator = simulator
        self.owner = None
        self.queue_tasks = queue.Queue()

    def lock(self, task):
        if self.owner:  # and self.owner != task:
            self.queue_tasks.put(task)
            self.simulator.suspend_task()
        else:
            self.owner = task

    def unlock(self, task):
        if task == self.owner:
            self.owner = None
            if not self.queue_tasks.empty():
                task_to_awake = self.queue_tasks.get()
                self.simulator.unsuspend_task(task_to_awake)
