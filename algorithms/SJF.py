from lib.Scheduler import Scheduler
from lib.Process import Process

class SJF(Scheduler):
    def __init__(self, preemptive: bool = False):
        super().__init__(preemptive=preemptive)

    def pick(self, ready, processes):
        # Non-preemptive: sort by original burst time
        # Preemptive (SRTF): sort by remaining time
        key = lambda p: (p.remaining_time if self.preemptive else p.burst_time, p.arrival_time)
        return min(ready, key=key)