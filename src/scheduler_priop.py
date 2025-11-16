
class Scheduler():
    def __init__(self,
        simulator
    ):
        self.simulator = simulator

    def execute(self):
        # Find the one with the maximum priority value
        priority_task = max(self.simulator.list_tasks_existing, key=lambda t: t.priority, default=None)
            
        # Find the highest priority new task
        priority_task_new = max(self.simulator.list_tasks_new, key=lambda t: t.priority, default=None)
        
        # 4. Decide whether to preempt
        if (priority_task_new and
            (priority_task and priority_task_new.priority > priority_task.priority or
            not priority_task)
        ):
            # A new task has arrived with a higher priority
            if self.simulator.current_task:
                self.simulator.preempt_task(self.simulator.current_task)
            self.simulator.schedule_task(priority_task_new)
        elif priority_task and not self.simulator.current_task:
            # No new tasks, just run the highest priority "ready" task
            self.simulator.schedule_task(priority_task)
