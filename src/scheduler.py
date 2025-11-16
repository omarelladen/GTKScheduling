import os

class Scheduler():
    def __init__(self,
        simulator
    ):
        self.simulator = simulator
        self.current_task = None

    def _exe_rr(self):
        # Round Robin (RR)

        # 1. Enqueue new tasks
        for task in self.simulator.list_tasks:
            if task.state == None and task.start_time <= self.simulator.time:
                task.state = "ready"
                self.simulator.queue_tasks.put(task)

        # 2. Check for preemption or task completion
        # This happens if the quantum is used up OR the current task finished
        if self.simulator.used_quantum % self.simulator.quantum == 0 or (self.current_task and self.current_task.progress == self.current_task.duration):
            if self.current_task:
                if self.current_task.progress == self.current_task.duration:
                    # Task finished
                    self.current_task.state = "terminated"
                    self.simulator.num_term_tasks += 1
                    self.simulator.used_quantum = 0
                else:
                    # Quantum expired, re-queue the task
                    self.current_task.state = "ready"
                    self.simulator.queue_tasks.put(self.current_task)
                    self.simulator.used_quantum = 0

            # 3. Get next task from the queue
            if not self.simulator.queue_tasks.empty():
                self.current_task = self.simulator.queue_tasks.get()
                self.current_task.state = "running"
            else:
                self.current_task = None
                self.simulator.used_quantum = 0  # reset quantum

    def _exe_srtf(self):
        # Shortest Remaining Time First (SRTF)

        # 1. Check if the current task finished
        if self.current_task:
            if self.current_task.progress == self.current_task.duration:
                self.current_task.state = "terminated"
                self.simulator.num_term_tasks += 1
                self.current_task = None
        
        # 2. Find the shortest ready task
        # Get all tasks that are waiting or currently running
        list_tasks_ready = [t for t in self.simulator.list_tasks if (t.state == "ready" or t.state == "running") and t.duration != t.progress]
        # Find the one with the minimum (duration - progress)
        shortest_task = min(list_tasks_ready, key=lambda t: t.duration - t.progress, default=None)

        list_tasks_new = []
        # 3. Check for newly arriving tasks
        for task in self.simulator.list_tasks:
            if task.state == None and task.start_time <= self.simulator.time:
                task.state = "ready"
                list_tasks_new.append(task)
        # Find the shortest new task (based on total duration)
        shortest_task_new = min(list_tasks_new, key=lambda t: t.duration, default=None)

        # 4. Decide whether to preempt
        if ((shortest_task_new and shortest_task and shortest_task_new.duration < shortest_task.duration - shortest_task.progress) or
            (shortest_task_new and shortest_task == None)):
            # A new task has arrived that is shorter than the remaining time of the shortest waiting task
            if self.current_task:
                self.current_task.state = "ready"  # preempt
            self.current_task = shortest_task_new
            self.current_task.state = "running"
        elif shortest_task and self.current_task == None:
            # No new tasks, just run the shortest ready task
            self.current_task = shortest_task
            self.current_task.state = "running"

    def _exe_priop(self):
        # Preemptive Priority (PRIOp)
        
        # 1. Check if the current task finished
        if self.current_task:
            if self.current_task.progress == self.current_task.duration:
                self.current_task.state = "terminated"
                self.simulator.num_term_tasks += 1
                self.current_task = None
        
        # 2. Find the highest priority ready task
        # Get all tasks that are waiting or currently running
        list_tasks_ready = [t for t in self.simulator.list_tasks if (t.state == "ready" or t.state == "running") and t.duration != t.progress]
        # Find the one with the maximum priority value
        shortest_task = max(list_tasks_ready, key=lambda t: t.priority, default=None)

        list_tasks_new = []
        # 3. Check for newly arriving tasks
        for task in self.simulator.list_tasks:
            if task.state == None and task.start_time <= self.simulator.time:
                task.state = "ready"
                list_tasks_new.append(task)
        # Find the highest priority new task
        shortest_task_new = max(list_tasks_new, key=lambda t: t.priority, default=None)

        # 4. Decide whether to preempt
        if ((shortest_task_new and shortest_task and shortest_task_new.priority > shortest_task.priority) or
            (shortest_task_new and shortest_task == None)):
            # A new task has arrived with a higher priority
            if self.current_task:
                self.current_task.state = "ready"  # Preempt
            self.current_task = shortest_task_new
            self.current_task.state = "running"
        elif shortest_task and self.current_task == None:
            # No new tasks, just run the highest priority "ready" task
            self.current_task = shortest_task
            self.current_task.state = "running"
