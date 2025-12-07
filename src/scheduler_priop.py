import random

class Scheduler():
    def __init__(self,
        simulator
    ):
        self.simulator = simulator

    def execute(self):

        list_all_tasks = self.simulator.list_tasks_previous + self.simulator.list_tasks_new
        
        # Find the one with the maximum priority
        priority_task = max(
            list_all_tasks,
            key=lambda t: (
                t.priority,          # higher static priority
                len(t.state),        # give priority to the current task
                (-1)*t.start_time,   # lower start time
                (-1)*t.duration,     # lower duration
                random.random()      # random tiebreaker
            ),
            default=None
        )


        # def is_tiebreak_random(task, max_task):
        #     return (
        #         task.priority == max_task.priority and
        #         len(task.state) == len(max_task.state) and
        #         task.start_time == max_task.start_time and
        #         task.duration == max_task.duration
        #     )
        # 
#         if priority_task:
#             list_tasks_tied = [t for t in list_all_tasks if is_tiebreak_random(t, priority_task)]
#             print(list_tasks_tied)
# 
#             if len(list_all_tasks) > 1:
#                 print("Random")
#             else:
#                 print("No random")


        if priority_task:  # there is a task in the system
            if self.simulator.current_task and priority_task != self.simulator.current_task:
                self.simulator.preempt_task(self.simulator.current_task)
                self.simulator.schedule_task(priority_task)
            elif not self.simulator.current_task:
                self.simulator.schedule_task(priority_task)
