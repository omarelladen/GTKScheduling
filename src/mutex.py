import queue

class Mutex():
    def __init__(self,
        id,
        simulator
    ):
        self.id = id
        self.simulator = simulator
        self.owner = None
        self.queue = queue.Queue()

    def lock(self, task):
        if self.owner:
            self.queue.put(task)
            self.simulator.suspend_task()
        else:
            self.owner = task

    def unlock(self, task):
        if task == self.owner:
            task_to_awake = self.queue.get()
            unsuspend_task(self.queue)
