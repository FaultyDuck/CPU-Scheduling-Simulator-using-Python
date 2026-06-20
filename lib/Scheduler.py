from abc import ABC, abstractmethod
from typing import List, Optional
from lib.Process import Process

class Scheduler(ABC):
    def __init__(self, time_quantum: Optional[int] = None, preemptive: bool = False):
        self.log: List[dict] = []
        self.t: int = 0
        self.quantum = time_quantum
        self.preemptive = preemptive
        self.current: Optional[Process] = None
        self.processes: List[Process] = []

    def setup(self, processes: List[Process]):
        self.log, self.t = [], 0
        self.current = None
        self.processes = processes

    def run_tick(self, processes, current_time, execution_log):
        if current_time == 0: # on the first tick, convert dicts to process
            self.setup([
                Process(p["pid"], p["arrival_time"], p["burst_time"], p["priority"])
                for p in processes
            ])

        entry = self.tick_once()
        if entry:
            execution_log.append(entry)

        # syncs status from process object back to the dict for reuslt table
        for p_dict, p_obj in zip(processes, self.processes):
            p_dict["completed"] = p_obj.completed
            p_dict["completion_time"] = p_obj.completion_time

        return all(p.completed for p in self.processes)

    def tick_once(self) -> dict:
        if all(p.completed for p in self.processes):
            return None

        # get all processes that have arrived and are not completed
        ready = [p for p in self.processes if p.arrival_time <= self.t and not p.completed]

        # if no processes are ready, log idle time
        if not ready:
            entry = {"time": self.t, "pid": "Idle"}
            self.log.append(entry)
            self.t += 1
            return entry

        # if preemptive or no current process, pick a new one
        if self.preemptive or self.current is None or self.current.completed:
            self.current = self.pick(ready, self.processes)

        # execute the current process for one tick
        p = self.pick(ready, self.processes)
        entry = {"time": self.t, "pid": p.pid}
        self.log.append(entry)
        p.remaining_time -= 1
        self.t += 1

        # if the process is completed mark it and record completion time
        if p.remaining_time <= 0:
            p.completed = True
            p.completion_time = self.t
        else:
            self.tick(p, self.processes)

        return entry

    def schedule(self, processes: List[Process]) -> List[dict]:
        self.setup(processes)
        while self.tick_once() is not None:
            pass
        return self.log

    @abstractmethod
    def pick(self, ready: List[Process], processes: List[Process]) -> Process:
        pass

    def tick(self, process: Process, processes: List[Process]):
        pass
