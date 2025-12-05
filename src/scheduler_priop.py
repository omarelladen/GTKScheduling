
class Scheduler():
    def __init__(self,
        simulator
    ):
        self.simulator = simulator

    def execute(self):
        # Find the one with the maximum priority value
        priority_task = max(
            self.simulator.list_tasks_previous,
            key=lambda t: t.priority,
            default=None
        )
            
        # Find the highest priority new task
        priority_task_new = max(
            self.simulator.list_tasks_new,
            key=lambda t: t.priority,
            default=None
        )
        
        # New task has arrived with higher priority than the previous ones
        if (priority_task_new and
            (priority_task and priority_task_new.priority > priority_task.priority or
            not priority_task)
        ):
            # Preempt the current task if it exists
            if self.simulator.current_task:
                self.simulator.preempt_task(self.simulator.current_task)

            self.simulator.schedule_task(priority_task_new)

        # No new tasks, run the highest priority between the previous ones
        elif priority_task and not self.simulator.current_task:
            self.simulator.schedule_task(priority_task)
