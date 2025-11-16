
class Scheduler():
    def __init__(self,
        simulator
    ):
        self.simulator = simulator

    def exe_rr(self):
        # Get next task from the queue
        if not self.simulator.queue_tasks.empty():
            self.simulator.schedule_task(self.simulator.queue_tasks.get())

    def exe_srtf(self):
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


    def exe_priop(self):
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
