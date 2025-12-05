
class Task():
    def __init__(self,
        id,
        color_hex,
        start_time,
        duration,
        priority,
        state = None,
        progress = 0,
        turnaround_time = 0,
        waiting_time = 0
    ):
        self.id = id
        self.color_hex = color_hex
        self.start_time = start_time
        self.duration = duration
        self.priority = priority
        self.state = state
        self.progress = progress
        self.turnaround_time = turnaround_time
        self.waiting_time = waiting_time

        self.dynamic_priority = self.priority

    def terminate(self):
        self.state = "terminated"

    def preempt(self):
        self.state = "ready"
        self.dynamic_priority = self.priority

    def load(self):
        self.state = "ready"

    def schedule(self):
        self.state = "running"

    def update_ready(self):
        self.waiting_time += 1
        self.turnaround_time += 1

    def update_ready_when_scheduling(self):
        self.dynamic_priority += 1

    def execute(self):
        self.progress += 1
        self.turnaround_time += 1
