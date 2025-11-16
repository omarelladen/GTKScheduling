import os

class Scheduler():
    def __init__(self,
        simulator
    ):
        self.simulator = simulator
        self.list_tasks_new = []
        self.list_tasks_existing = []

    def monitor_rr(self):
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

    def exe_rr(self):
        # Get next task from the queue
        if not self.simulator.queue_tasks.empty():
            self.simulator.schedule_task(self.simulator.queue_tasks.get())

    def monitor_srtf(self):
        # Shortest Remaining Time First (SRTF)

        interrupt = False

        # 1. Check if the current task finished
        if self.simulator.current_task and self.simulator.current_task.progress == self.simulator.current_task.duration:
            self.simulator.terminate_task(self.simulator.current_task)
            interrupt = True
                
        # 2. Get all tasks that are waiting or currently running
        self.list_tasks_existing = [
            t for t in self.simulator.list_tasks
            if t.state == "ready" or t.state == "running"
        ]

        # 3. Check for newly arriving tasks
        self.list_tasks_new = []
        for task in self.simulator.list_tasks:
            if not task.state and task.start_time <= self.simulator.time:
                self.simulator.load_new_task(task)
                self.list_tasks_new.append(task)
                interrupt = True

        return interrupt

    def exe_srtf(self):
        # Find the one with the minimum (duration - progress)
        shortest_task = min(self.list_tasks_existing, key=lambda t: t.duration - t.progress, default=None)

        # Find the shortest new task (based on total duration)
        shortest_task_new = min(self.list_tasks_new, key=lambda t: t.duration, default=None)
            
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

    def monitor_priop(self):
        # Preemptive Priority (PRIOp)

        interrupt = False

        # 1. Check if the current task finished
        if self.simulator.current_task and self.simulator.current_task.progress == self.simulator.current_task.duration:
            self.simulator.terminate_task(self.simulator.current_task)
            interrupt = True
        
        # 2. Get all tasks that are waiting or currently running
        self.list_tasks_existing = [
            t for t in self.simulator.list_tasks
            if t.state == "ready" or t.state == "running"
        ]

        # 3. Check for newly arriving tasks
        self.list_tasks_new = []
        for task in self.simulator.list_tasks:
            if not task.state and task.start_time <= self.simulator.time:
                self.simulator.load_new_task(task)
                self.list_tasks_new.append(task)
                interrupt = True

        return interrupt

    def exe_priop(self):
        # Find the one with the maximum priority value
        priority_task = max(self.list_tasks_existing, key=lambda t: t.priority, default=None)
            
        # Find the highest priority new task
        priority_task_new = max(self.list_tasks_new, key=lambda t: t.priority, default=None)
        
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
