from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

class Scheduler(ABC):
    def __init__(self, time_quantum: Optional[int] = None):
        self.log: List[dict] = []
        self.t: int = 0
        self.quantum = time_quantum

    def schedule(self, processes: List[Process]) -> List[dict]:
        self.log, self.t = [], 0
        
        while not all(p.completed for p in processes):
            # only consider processes that alr arrived and not completed
            ready = [p for p in processes if p.arrival_time <= self.t and not p.completed] 
            
            # if no process is ready, log idle time and move to next tick
            if not ready:
                self.log.append({"time": self.t, "pid": "Idle"})
                self.t += 1
                continue
            
            # pick the next process to run based on the scheduling algorithm and move tiem forward
            p = self.pick(ready, processes)
            self.log.append({"time": self.t, "pid": p.pid})
            p.remaining_time -= 1
            self.t += 1
            
            # if current process is done, do the finish stuff, else just move time forward
            if p.remaining_time <= 0:
                p.completed = True
                p.completion_time = self.t
            else:
                self.tick(p, processes)
        
        return self.log

    @abstractmethod
    def pick(self, ready: List[Process], processes: List[Process]) -> Process:
        """Select the next process to run, must be implemented by other algos"""
        pass

    def tick(self, process: Process, processes: List[Process]):
        """Post-processing after a tick, only used by RR"""
        pass

