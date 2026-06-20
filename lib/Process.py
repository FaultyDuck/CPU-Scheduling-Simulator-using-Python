from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Process:
    pid: str
    arrival_time: int
    burst_time: int
    priority: int = 0
    remaining_time: int = field(init=False)
    completed: bool = field(default=False, init=False)
    completion_time: Optional[int] = field(default=None, init=False)

    def __post_init__(self):
        self.remaining_time = self.burst_time
