from lib.Scheduler import Scheduler
from lib.Process import Process

class FCFS(Scheduler):
    def __init__(self):
        super().__init__(preemptive=False)
    def pick(self, ready, processes):
        return min(ready, key=lambda p: (p.arrival_time, p.pid))