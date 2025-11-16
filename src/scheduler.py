import os

class Scheduler():
    def __init__(self,
        simulator
    ):
        self.simulator = simulator
        self.current_task = None
        self.interrupt = False
        self.list_tasks_new = []
        self.list_tasks_existing = []

    def monitor_rr(self):
        # Round Robin (RR)

        # 1. Enqueue new tasks
        for task in self.simulator.list_tasks:
            if not task.state and task.start_time <= self.simulator.time:
                task.state = "ready"
                self.simulator.queue_tasks.put(task)

        # 2. Check if current task finished
        if self.current_task and self.current_task.progress == self.current_task.duration:
            self.current_task.state = "terminated"
            self.simulator.num_term_tasks += 1
            self.current_task = None
            self.simulator.used_quantum = 0

            self.interrupt = True

        # 3. Check if quantum expired
        if self.simulator.used_quantum % self.simulator.quantum == 0:
            if self.current_task:
                self.current_task.state = "ready"
                self.simulator.queue_tasks.put(self.current_task)
                self.simulator.used_quantum = 0

            self.interrupt = True

    def exe_rr(self):
        # Get next task from the queue
        if not self.simulator.queue_tasks.empty():
            self.current_task = self.simulator.queue_tasks.get()
            self.current_task.state = "running"

    def monitor_srtf(self):
        # Shortest Remaining Time First (SRTF)

        # 1. Check if the current task finished
        if self.current_task and self.current_task.progress == self.current_task.duration:
            self.current_task.state = "terminated"
            self.simulator.num_term_tasks += 1
            self.current_task = None

            self.interrupt = True
                
        # 2. Get all tasks that are waiting or currently running
        self.list_tasks_existing = [
            t for t in self.simulator.list_tasks
            if (t.state == "ready" or t.state == "running") and t.duration != t.progress
        ]

        # 3. Check for newly arriving tasks
        self.list_tasks_new = []
        for task in self.simulator.list_tasks:
            if not task.state and task.start_time <= self.simulator.time:
                task.state = "ready"
                self.list_tasks_new.append(task)

                self.interrupt = True

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
            if self.current_task:
                self.current_task.state = "ready"  # preempt
            self.current_task = shortest_task_new
            self.current_task.state = "running"
        elif shortest_task and not self.current_task:
            # No new tasks, just run the shortest ready task
            self.current_task = shortest_task
            self.current_task.state = "running"

    def monitor_priop(self):
        # Preemptive Priority (PRIOp)
        
        # 1. Check if the current task finished
        if self.current_task and self.current_task.progress == self.current_task.duration:
            self.current_task.state = "terminated"
            self.simulator.num_term_tasks += 1
            self.current_task = None

            self.interrupt = True
        
        # 2. Get all tasks that are waiting or currently running
        self.list_tasks_existing = [
            t for t in self.simulator.list_tasks
            if (t.state == "ready" or t.state == "running") and t.duration != t.progress
        ]

        # 3. Check for newly arriving tasks
        self.list_tasks_new = []
        for task in self.simulator.list_tasks:
            if not task.state and task.start_time <= self.simulator.time:
                task.state = "ready"
                self.list_tasks_new.append(task)

                self.interrupt = True

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
            if self.current_task:
                self.current_task.state = "ready"  # Preempt
            self.current_task = priority_task_new
            self.current_task.state = "running"
        elif priority_task and not self.current_task:
            # No new tasks, just run the highest priority "ready" task
            self.current_task = priority_task
            self.current_task.state = "running"
