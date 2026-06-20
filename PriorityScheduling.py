def priorityScheduling(processes, current_time, execution_log):
    queue = [p for p in processes]
    queue.sort(key=lambda x: x["priority"]) #sort by priority

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

    all_done = all(p["completed"] for p in processes)
    return all_done