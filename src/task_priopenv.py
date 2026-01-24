
from .task import Task

class Task(Task):
    def __init__(
        self,
        id,
        color_hex,
        start_time,
        duration,
        priority,
        list_events = []
    ):
        super().__init__(
            id,
            color_hex,
            start_time,
            duration,
            priority,
            list_events
        )

        self.dynamic_priority = self.priority

    def schedule(self):
        self.state = "running"
        self.dynamic_priority = self.priority

    def preempt(self):
        self.state = "ready"
        self.dynamic_priority = self.priority

    def update_ready_when_scheduling(self, alpha):
        self.dynamic_priority += alpha
