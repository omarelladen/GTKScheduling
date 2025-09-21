
class Task():
    def __init__(self,
        id,
        color_num,
        start_time,
        duration,
        priority
    ):
        self.id = id
        self.color_num = color_num
        self.start_time = start_time
        self.duration = duration
        self.priority = priority
        self.progress = 0
        self.state = ''
