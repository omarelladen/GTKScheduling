
class Scheduler():
    def __init__(self,
        simulator
    ):
        self.simulator = simulator

    def execute(self):
        # Find the one with the minimum (duration - progress)
        shortest_task = min(self.simulator.list_tasks_existing, key=lambda t: t.duration - t.progress, default=None)

        # Find the shortest new task (based on total duration)
        shortest_task_new = min(self.simulator.list_tasks_new, key=lambda t: t.duration, default=None)
            
        # Decide whether to preempt
        if (shortest_task_new and
            (shortest_task and shortest_task_new.duration < shortest_task.duration - shortest_task.progress or
            not shortest_task)
        ):
            # A new task has arrived that is shorter than the remaining time of the shortest waiting task
            if self.simulator.current_task:
                self.simulator.preempt_task(self.simulator.current_task)
            self.simulator.schedule_task(shortest_task_new)
        elif shortest_task and not self.simulator.current_task:
            # No new tasks, just run the shortest ready task
            self.simulator.schedule_task(shortest_task)
