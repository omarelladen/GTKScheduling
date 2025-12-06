
from .task import Task

class Task(Task):
    def __init__(self,
        id,
        color_hex,
        start_time,
        duration,
        priority
    ):
        # Inherited:
        self.id = id
        self.color_hex = color_hex
        self.start_time = start_time
        self.duration = duration
        self.priority = priority
        self.state = None
        self.progress = 0
        self.turnaround_time = 0
        self.waiting_time = 0

        self.dynamic_priority = self.priority

    def preempt(self):
        self.state = "ready"
        self.dynamic_priority = self.priority

    def update_ready_when_scheduling(self, alpha):
        self.dynamic_priority += alpha
