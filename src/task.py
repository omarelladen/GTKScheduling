
class Task():
    def __init__(self,
        id,
        color_num,
        start_time,
        duration,
        priority,
        state = None,
        progress = 0,
        turnaround_time = 0,
        waiting_time = 0
    ):
        self.id = id
        self.color_num = color_num
        self.start_time = start_time
        self.duration = duration
        self.priority = priority
        self.state = state
        self.progress = progress
        self.turnaround_time = turnaround_time
        self.waiting_time = waiting_time

    def execute(self):
        self.progress += 1
        self.turnaround_time += 1
