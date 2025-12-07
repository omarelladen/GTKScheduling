
class Task():
    def __init__(self,
        id,
        color_hex,
        start_time,
        duration,
        priority,
        list_io = []
    ):
        self.id = id
        self.color_hex = color_hex
        self.start_time = start_time
        self.duration = duration
        self.priority = priority
        self.list_io = list_io
        self.list_ongoing_io = []
        self.state = None
        self.progress = 0
        self.turnaround_time = 0
        self.waiting_time = 0
        self.io_progress = 0

    def terminate(self):
        self.state = "terminated"

    def preempt(self):
        self.state = "ready"
        print("preempted", self.id)

    def suspend(self):
        self.state = "suspended"

    def load(self):
        self.state = "ready"

    def unsuspend(self):
        self.state = "ready"

    def schedule(self):
        self.state = "running"

    def update_ready(self):
        self.waiting_time += 1
        print("update_ready-waiting_time++")

    def update_suspended(self):
        self.waiting_time += 1
        print("update_suspended-waiting_time++")
        self.io_progress += 1

    def update_ready_when_scheduling(self, alpha):
        pass

    def execute(self, simulator):
        io_execution = False
        for event in self.list_io.copy():  # copy - bc events can be removed inside the loop
            if event[0] == "io" and self.progress == event[1]:
                print("io", self.id, event[1], event[2])
                io_execution = True
                self.list_ongoing_io.append(event)
                self.list_io.remove(event)
                simulator.io_req()
            elif event[0] == "ml" and self.progress == event[2]:
                print("ml", event[1])
                simulator.ml_req(event[1])
            elif event[0] == "mu" and self.progress == event[2]:
                print("mu", event[1])
                simulator.mu_req(event[1])

        if not io_execution:
            self.progress += 1
            simulator.used_quantum += 1
        else:
            self.io_progress += 1

