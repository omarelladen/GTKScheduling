import random

class Scheduler():
    def __init__(self,
        simulator
    ):
        self.simulator = simulator

    def execute(self):

        list_all_tasks = self.simulator.list_tasks_previous + self.simulator.list_tasks_new
        
        # Find the one with the maximum priority
        priority_task = max(
            list_all_tasks,
            key=lambda t: (
                t.priority,          # higher static priority
                len(t.state),        # give priority to the current task
                (-1)*t.start_time,   # lower start time
                (-1)*t.duration,     # lower duration
                random.random()      # random tiebreaker
            ),
            default=None
        )

        if priority_task:  # there is a task in the system
            if self.simulator.current_task and priority_task != self.simulator.current_task:
                self.simulator.preempt_task(self.simulator.current_task)
                self.simulator.schedule_task(priority_task)
            elif not self.simulator.current_task:
                self.simulator.schedule_task(priority_task)
