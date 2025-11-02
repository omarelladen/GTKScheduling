
class TaskRecord():
    def __init__(self,
        task,
        state,
        progress,
        turnaround_time,
        waiting_time,
        time
    ):
        self.task = task
        self.state = state
        self.progress = progress
        self.turnaround_time = turnaround_time
        self.waiting_time = waiting_time
        self.time = time
