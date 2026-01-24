
class Scheduler():
    def __init__(
        self,
        simulator
    ):
        self.simulator = simulator

    def execute(self):
        # Get next task from the queue
        if not self.simulator.queue_tasks.empty():
            next_task = self.simulator.queue_tasks.get()
            self.simulator.schedule_task(next_task)
