def FCFS(processes, current_time, execution_log):
    queue = [p for p in processes if p["arrival_time"] <= current_time and not p["completed"]]
    queue.sort(key=lambda x: x["arrival_time"])

    if not queue:
        execution_log.append({"time": current_time, "pid": "Idle"})
        return False

    processing = queue[0]

    if processing["remaining_time"] == 0:
        processing["remaining_time"] = processing["burst_time"]

    execution_log.append({"time": current_time, "pid": processing["pid"]})
    processing["remaining_time"] -= 1

    if processing["remaining_time"] <= 0:
        processing["completed"] = True
        processing["completion_time"] = current_time + 1

    return all(p["completed"] for p in processes)