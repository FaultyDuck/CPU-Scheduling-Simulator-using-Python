from lib.Scheduler import Scheduler
from lib.Process import Process

class PriorityScheduling(Scheduler):
    def __init__(self, preemptive: bool = False):
        super().__init__(preemptive=preemptive)

    def pick(self, ready, processes):
        return min(ready, key=lambda p: (p.priority, p.arrival_time))