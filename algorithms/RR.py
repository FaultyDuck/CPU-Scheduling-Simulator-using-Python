from lib.Scheduler import Scheduler
from lib.Process import Process

class RR(Scheduler):
    def __init__(self, quantum: int):
        super().__init__(preemptive=True, time_quantum=quantum)

    def pick(self, ready, processes):
        return min(ready, key=lambda p: p.arrival_time)

    def tick(self, p, processes):
        # if current time is a multiple of the quantum, move the current process to the end of the queue
        if self.quantum and self.t % self.quantum == 0:
            processes.append(processes.pop(processes.index(p)))