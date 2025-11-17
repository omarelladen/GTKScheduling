
class Scheduler():
    def __init__(self,
        simulator
    ):
        self.simulator = simulator

    def execute(self):
        # Find the one with the minimum (duration - progress)
        shortest_task = min(self.simulator.list_tasks_previous, key=lambda t: t.duration - t.progress, default=None)

        # Find the shortest new task (based on total duration)
        shortest_task_new = min(self.simulator.list_tasks_new, key=lambda t: t.duration, default=None)
            
        # New task has arrived that is shorter than the remaining time of the previous ones
        if (shortest_task_new and
            (shortest_task and shortest_task_new.duration < shortest_task.duration - shortest_task.progress or
            not shortest_task)
        ):
            # Preempt the current task if it exists
            if self.simulator.current_task:
                self.simulator.preempt_task(self.simulator.current_task)
            
            self.simulator.schedule_task(shortest_task_new)

        # No new tasks, run the shortest ready between previous ones
        elif shortest_task and not self.simulator.current_task:
            self.simulator.schedule_task(shortest_task)
