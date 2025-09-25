from task import Task

class Scheduler():
    def __init__(self, tasks_path):
        # Scheduling parameters
        self.alg_scheduling, self.quantum = self._setup_scheduling(tasks_path)
        self.list_tasks = self._setup_tasks(tasks_path)
        self.num_tasks = len(self.list_tasks)
        self.time = 0
        self.current_task = self.list_tasks[0]

    def tick(self):
        # Update time
        self.time += 1;

        # Update task info
        self.current_task.progress += 1
        for task in self.list_tasks:
            if task != self.current_task:
                task.state = 'ready'
        self.current_task.state = 'running'

        old_task = self.current_task
        
        # Change or not the current task
        if self.time % self.quantum == 0:
            if self.current_task.id == self.num_tasks:
                self.current_task = self.list_tasks[0]
            else:
                self.current_task = self.list_tasks[self.current_task.id]

        return old_task

    def _setup_scheduling(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        alg_scheduling = lines[0].split(";")[0]
        quantum = int(lines[0].split(";")[1])
    
        return alg_scheduling, quantum

    def _setup_tasks(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        list_tasks = []
        for line in lines[1:]:            
            task_id         = int(line.split(";")[0].replace("t", ""))                
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

        return list_tasks
