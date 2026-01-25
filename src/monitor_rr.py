import random


class Monitor():
    def __init__(
        self,
        simulator
    ):
        self.simulator = simulator

    def execute(self):

        interrupt = False

        # Sort new tasks
        list_tasks_ready = [
            t for t in self.simulator.list_tasks
            if not t.state and t.start_time <= self.simulator.time
        ]

        list_tasks_ready.sort(
            key=lambda t: (
                (-1)*t.duration,  # lower duration
                random.random()   # random tiebreaker
            ),
            reverse=False
        )

        # 1. Enqueue new tasks
        for task in list_tasks_ready:
            self.simulator.load_task(task)
            self.simulator.queue_tasks.put(task)

        # 2. Check if current task finished
        if (self.simulator.current_task and
            self.simulator.current_task.progress == self.simulator.current_task.duration
        ):
            self.simulator.terminate_task(self.simulator.current_task)
            interrupt = True

        # 3. Check if quantum expired
        if self.simulator.used_quantum % self.simulator.quantum == 0:
            if self.simulator.current_task:
                self.simulator.preempt_task(self.simulator.current_task)
                self.simulator.queue_tasks.put(self.simulator.current_task)
            interrupt = True

        return interrupt
