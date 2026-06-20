import random

def generate_random_processes(num_processes=5, start_id=1):
    processes = []
    for i in range(start_id, start_id + num_processes):
        processes.append({
            "pid": f"P{i}",
            "arrival_time": random.randint(0, 5),
            "burst_time": random.randint(2, 8),
            "remaining_time": 0,
            "priority": random.randint(1, 5),
            "completed": False,
            "completion_time": 0,
        })
    return processes