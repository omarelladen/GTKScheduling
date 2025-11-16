
class Monitor():
    def __init__(self,
        simulator
    ):
        self.simulator = simulator

    def execute(self):
        # Round Robin (RR)

        interrupt = False

        # 1. Enqueue new tasks
        for task in self.simulator.list_tasks:
            if not task.state and task.start_time <= self.simulator.time:
                self.simulator.load_new_task(task)
                self.simulator.queue_tasks.put(task)

        # 2. Check if current task finished
        if self.simulator.current_task and self.simulator.current_task.progress == self.simulator.current_task.duration:
            self.simulator.terminate_task(self.simulator.current_task)
            interrupt = True

        # 3. Check if quantum expired
        if self.simulator.used_quantum % self.simulator.quantum == 0:
            if self.simulator.current_task:
                self.simulator.preempt_task(self.simulator.current_task)
                self.simulator.queue_tasks.put(self.simulator.current_task)
            interrupt = True

        return interrupt
