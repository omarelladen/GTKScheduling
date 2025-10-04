import os

from task import Task

class Scheduler():
    def __init__(self,
        tasks_path
    ):
        # Scheduling parameters
        self.alg_scheduling, self.quantum, self.list_tasks = self._setup_from_file(tasks_path)
        self.num_tasks = len(self.list_tasks)
        self.time = 0
        
        self.current_task = self.list_tasks[0]
        self.current_task.state = 'running'
        
    def update_current_task(self):
        self.time += 1
        self.current_task.progress += 1

    def fcfs(self):
        if self.time % self.quantum == 0:
            # Change to next (circular)
            self.current_task.state = 'ready'
            if self.current_task.id == self.num_tasks:
                self.current_task = self.list_tasks[0]  
            else:
                self.current_task = self.list_tasks[self.current_task.id]
            self.current_task.state = 'running'
                
    #New algorithms
    def rr(self):
        if self.time % self.quantum == 0:
            self.current_task.state = 'ready'
            next_index = (self.current_task.id) % self.num_tasks
            # Skip finished
            for _ in range(self.num_tasks):
                task = self.list_tasks[next_index]
                if task.state != 'finished':
                    self.current_task = task
                    break
                next_index = (next_index + 1) % self.num_tasks
            self.current_task.state = 'running'

    def sjf(self):
        if self.current_task.state == 'finished' or self.time == 0:
            #Choose the task with least duration
            ready_tasks = [t for t in self.list_tasks if t.state != 'finished']
            if ready_tasks:
                self.current_task = min(ready_tasks, key=lambda t: t.duration)
                self.current_task.state = 'running'

    def srtf(self):
        #Choose the task with least duration
        ready_tasks = [t for t in self.list_tasks if t.state != 'finished' and t.start_time <= self.time]
        if ready_tasks:
            shortest = min(ready_tasks, key=lambda t: t.duration - t.progress)
            if self.current_task != shortest:
                self.current_task.state = 'ready'
                self.current_task = shortest
                self.current_task.state = 'running'

    def prioc(self):
        if self.current_task.state == 'finished' or self.time == 0:
            ready_tasks = [t for t in self.list_tasks if t.state != 'finished']
            if ready_tasks:
                self.current_task = min(ready_tasks, key=lambda t: t.priority)
                self.current_task.state = 'running'

    def priop(self):
        ready_tasks = [t for t in self.list_tasks if t.state != 'finished']
        if ready_tasks:
            highest = min(ready_tasks, key=lambda t: t.priority)
            if self.current_task != highest:
                self.current_task.state = 'ready'
                self.current_task = highest
                self.current_task.state = 'running'

    def priod(self):
        #Increment priority
        for t in self.list_tasks:
            if t.state == 'ready':
                t.priority = max(1, t.priority - 1) #Considering 1 as the most important

        ready_tasks = [t for t in self.list_tasks if t.state != 'finished']
        if ready_tasks:
            chosen = min(ready_tasks, key=lambda t: t.priority)
            if self.current_task != chosen:
                self.current_task.state = 'ready'
                self.current_task = chosen
                self.current_task.state = 'running'
    
    def execute(self):
        if self.alg_scheduling == 'FCFS':
            self.fcfs()
        #New if cases
        elif self.alg_scheduling == 'RR':
            self.rr()
        elif self.alg_scheduling == 'SJF':
            self.sjf()
        elif self.alg_scheduling == 'SRTF':
            self.srtf()
        elif self.alg_scheduling == 'PRIOc':
            self.prioc()
        elif self.alg_scheduling == 'PRIOp':
            self.priop()
        elif self.alg_scheduling == 'PRIOd':
            self.priod()

    def _setup_from_file(self, file_path):
        # Default parameters
        default_alg_scheduling = 'FCFS'
        default_quantum = 2
        default_list_tasks = [Task(1,1,0,5,2),
                              Task(2,2,0,4,3),
                              Task(3,3,3,5,5),
                              Task(4,4,5,6,9),
                              Task(5,5,7,4,6)]
                                       
        if not os.path.isfile(file_path):
            return default_alg_scheduling, \
                   default_quantum, \
                   default_list_tasks
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) < 2:
            return default_alg_scheduling, \
                   default_quantum, \
                   default_list_tasks
                    
            
        alg_scheduling = lines[0].split(";")[0]
        quantum = int(lines[0].split(";")[1])
        
        list_tasks = []
        for line in lines[1:]:            
            task_id         = int(line.split(";")[0])              
            task_color_num  = int(line.split(";")[1])                
            task_start_time = int(line.split(";")[2])                
            task_duration   = int(line.split(";")[3])                
            task_priority   = int(line.split(";")[4])

            task = Task(task_id,
                        task_color_num,
                        task_start_time,
                        task_duration,
                        task_priority)

            list_tasks.append(task)

        return alg_scheduling, quantum, list_tasks
