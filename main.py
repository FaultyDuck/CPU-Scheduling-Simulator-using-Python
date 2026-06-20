import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from matplotlib.patches import Patch

from lib import randomGen
from algorithms import FCFS, PriorityScheduling, RR, SJF

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")


class CPUSimulator(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CPU Scheduling Simulator")
        self.geometry("1100x700")

        self.processes = []
        self.execution_log = []
        self.current_time = 0
        self.is_simulating = False
        self.pid_colors = {}

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.preemptive_var = ctk.BooleanVar()
        self.quantum_var = ctk.StringVar(value="2")
        self.algorithms = self.__initialize_algorithms()

        self.setup_ui_layout()
        self.setup_matplotlib_chart()

    def __initialize_algorithms(self):
        self.rr = RR.RR(quantum=int(self.quantum_var.get()))
        self.sjf = SJF.SJF()

        return {
            "Round Robin (RR)": self.rr.run_tick,
            "Shortest Job First (SJF)": self.sjf.run_tick,
        }


    def setup_ui_layout(self):
        # Row 1
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.pack(fill="x", padx=20, pady=(10, 5))

        ctk.CTkLabel(self.control_frame, text="Algorithm:").pack(side="left", padx=(10, 2))
        self.algo_var = ctk.StringVar(value="Priority Scheduling")
        self.algo_menu = ctk.CTkOptionMenu(
            self.control_frame, variable=self.algo_var,
            values=list(self.algorithms.keys()), width=180,
            command=lambda _: self._update_preemptive_state(),
        )
        self.algo_menu.pack(side="left", padx=5)

        self.preemptive_var = ctk.BooleanVar()
        self.preemptive_checkbox = ctk.CTkCheckBox(self.control_frame, text="Preemptive", variable=self.preemptive_var)
        self.preemptive_checkbox.pack(side="left", padx=5)
        self._update_preemptive_state()

        ctk.CTkLabel(self.control_frame, text="Time Quantum:").pack(side="left", padx=(15, 2))
        self.quantum_var = ctk.StringVar(value="2")
        self.quantum_entry = ctk.CTkEntry(self.control_frame, textvariable=self.quantum_var, width=50)
        self.quantum_entry.pack(side="left", padx=5)

        self.btn_start = ctk.CTkButton(
            self.control_frame, text="Start Simulation",
            command=self.on_start, state="disabled", text_color="Black",
        )
        self.btn_start.pack(side="right", padx=10, pady=10)

        self.topRightStatus = ctk.CTkLabel(self.control_frame, text="Status: Awaiting Data")
        self.topRightStatus.pack(side="right", padx=20)

        # Row 2
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(fill="x", padx=20, pady=5)

        # Random generation section
        ctk.CTkLabel(self.input_frame, text="Random Generate:").pack(side="left", padx=(10, 2))
        self.count_var = ctk.StringVar(value="5")
        self.count_entry = ctk.CTkEntry(self.input_frame, textvariable=self.count_var, width=45)
        self.count_entry.pack(side="left", padx=2)

        self.btn_generate = ctk.CTkButton(
            self.input_frame, text="Generate", command=self.on_generate, text_color="Black", width=90,
        )
        self.btn_generate.pack(side="left", padx=5)

        ctk.CTkLabel(self.input_frame, text="  |  Manual Add:").pack(side="left", padx=(15, 2))
        self.pid_var = ctk.StringVar()
        self.arrival_var = ctk.StringVar()
        self.burst_var = ctk.StringVar()
        self.priority_var = ctk.StringVar()

        for label, var, w in [("PID", self.pid_var, 60), ("Arrival", self.arrival_var, 55),
                               ("Burst", self.burst_var, 55), ("Priority", self.priority_var, 55)]:
            ctk.CTkLabel(self.input_frame, text=label + ":").pack(side="left", padx=(5, 1))
            ctk.CTkEntry(self.input_frame, textvariable=var, width=w).pack(side="left", padx=1)

        self.btn_add = ctk.CTkButton(
            self.input_frame, text="Add", command=self.on_add_manual, text_color="Black", width=60,
        )
        self.btn_add.pack(side="left", padx=5)

        self.btn_clear = ctk.CTkButton(
            self.input_frame, text="Clear All", command=self.on_clear, text_color="Black", width=80,
        )
        self.btn_clear.pack(side="left", padx=5)

        # Row 3
        self.display_frame = ctk.CTkFrame(self)
        self.display_frame.pack(fill="both", expand=True, padx=20, pady=5)

        self.txt_log = ctk.CTkTextbox(self.display_frame, width=280)
        self.txt_log.pack(side="left", fill="y", padx=10, pady=10)
        self.txt_log.insert("0.0", "Process Table:\nAdd or generate processes to begin.")

    def setup_matplotlib_chart(self):
        self.fig, self.ax = plt.subplots(figsize=(6, 3))
        self.fig.patch.set_facecolor('#2b2b2b')
        self.ax.set_facecolor('#1e1e1e')
        self.ax.tick_params(colors='white')
        self.ax.set_title("Gantt Chart", color='white')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.display_frame)
        self.canvas.get_tk_widget().pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def _update_preemptive_state(self):
        needs_preemptive = self.algo_var.get() in ["Shortest Job First (SJF)", "Priority Scheduling"]
        self.preemptive_checkbox.configure(state="normal" if needs_preemptive else "disabled")
        if not needs_preemptive:
            self.preemptive_var.set(False)

    def on_close(self):
        self.is_simulating = False
        self.quit()
        self.destroy()
        os._exit(0)

    # Process management
    def _get_next_pid(self):
        existing = [p["pid"] for p in self.processes]
        i = 1
        while f"P{i}" in existing:
            i += 1
        return f"P{i}"

    def on_generate(self):
        try:
            count = int(self.count_var.get())
        except ValueError:
            count = 5
        new_procs = randomGen.generate_random_processes(count, start_id=len(self.processes) + 1)
        self.processes.extend(new_procs)
        self.execution_log = []
        self.current_time = 0
        self._refresh_table()
        self.topRightStatus.configure(text="Status: Data Loaded – ready to Run")
        self.btn_start.configure(state="normal")
        self.redraw_gantt_chart()

    def on_add_manual(self):
        pid = self.pid_var.get().strip() or self._get_next_pid()
        try:
            arrival = int(self.arrival_var.get())
            burst = int(self.burst_var.get())
            priority = int(self.priority_var.get())
        except ValueError:
            self.topRightStatus.configure(text="Status: Invalid input – check numbers")
            return
        self.processes.append({
            "pid": pid,
            "arrival_time": arrival,
            "burst_time": max(1, burst),
            "remaining_time": 0,
            "priority": priority,
            "completed": False,
            "completion_time": 0,
        })
        self.execution_log = []
        self.current_time = 0
        self.pid_var.set("")
        self.arrival_var.set("")
        self.burst_var.set("")
        self.priority_var.set("")
        self._refresh_table()
        self.topRightStatus.configure(text="Status: Process added")
        self.btn_start.configure(state="normal")
        self.redraw_gantt_chart()

    def on_clear(self):
        self.processes.clear()
        self.execution_log.clear()
        self.pid_colors.clear()
        self.current_time = 0
        self.txt_log.delete("0.0", "end")
        self.txt_log.insert("0.0", "Process Table:\nAdd or generate processes to begin.")
        self.topRightStatus.configure(text="Status: Cleared")
        self.btn_start.configure(state="disabled")
        self.redraw_gantt_chart()

    def _refresh_table(self):
        self.txt_log.delete("0.0", "end")
        header = "PID\tArrival\tBurst\tPriority\n" + "-" * 40 + "\n"
        self.txt_log.insert("0.0", header)
        for p in self.processes:
            self.txt_log.insert("end", f"{p['pid']}\t{p['arrival_time']}\t{p['burst_time']}\t{p['priority']}\n")

    # Simulation
    def on_start(self):
        if not self.is_simulating and self.processes:
            self.sjf.preemptive = self.preemptive_var.get()
            for p in self.processes:
                p["remaining_time"] = 0
                p["completed"] = False
                p["completion_time"] = 0
            self.execution_log = []
            self.current_time = 0
            self.is_simulating = True
            self.btn_start.configure(state="disabled")
            self.btn_generate.configure(state="disabled")
            self.simulation_loop_tick()

    def simulation_loop_tick(self):
        if not self.is_simulating:
            return

        algo_name = self.algo_var.get()
        algo_fn = self.algorithms[algo_name]
        finished = algo_fn(self.processes, self.current_time, self.execution_log)

        current_tick_job = self.execution_log[-1]["pid"]
        self.topRightStatus.configure(text=f"Time: {self.current_time}ms | Active: {current_tick_job}")

        self.redraw_gantt_chart()

        self.current_time += 1

        if finished:
            self.is_simulating = False
            self.btn_start.configure(state="normal")
            self._show_results()
        else:
            self.after(100, self.simulation_loop_tick)

    # Results
    def _show_results(self):
        self.txt_log.delete("0.0", "end")

        # Compute completion times from execution_log
        for p in self.processes:
            p["completion_time"] = 0
        for entry in reversed(self.execution_log):
            pid = entry["pid"]
            if pid == "Idle":
                continue
            for p in self.processes:
                if p["pid"] == pid and p["completion_time"] == 0:
                    p["completion_time"] = entry["time"] + 1

        total_tat = 0
        total_wt = 0
        lines = ["PID\tAT\tBT\tCT\tTAT\tWT\n", "-" * 55 + "\n"]
        for p in self.processes:
            ct = p["completion_time"]
            tat = ct - p["arrival_time"]
            wt = tat - p["burst_time"]
            total_tat += tat
            total_wt += wt
            lines.append(f"{p['pid']}\t{p['arrival_time']}\t{p['burst_time']}\t{ct}\t{tat}\t{wt}\n")

        n = len(self.processes)
        avg_tat = total_tat / n if n else 0
        avg_wt = total_wt / n if n else 0

        lines.append("\n" + "-" * 55 + "\n")
        lines.append(f"Average Turnaround Time: {avg_tat:.2f}\n")
        lines.append(f"Average Waiting Time:    {avg_wt:.2f}\n")

        self.txt_log.insert("0.0", "".join(lines))
        self.topRightStatus.configure(text=f"Simulation Complete at {self.current_time}ms!")

    # Gantt chart
    def redraw_gantt_chart(self):
        self.ax.clear()
        self.ax.set_facecolor('#1e1e1e')
        self.ax.tick_params(colors='white')
        self.ax.set_xlabel("Time Units", color='white')
        self.ax.set_yticks([])

        if not self.execution_log:
            self.ax.set_title("Gantt Chart", color='white')
            self.canvas.draw()
            return

        # Merge consecutive same-process ticks into continuous blocks
        blocks = []
        for entry in self.execution_log:
            pid = entry["pid"]
            t = entry["time"]
            if blocks and blocks[-1]["pid"] == pid:
                blocks[-1]["end"] = t + 1
            else:
                blocks.append({"pid": pid, "start": t, "end": t + 1})

        # Assign random colours to PIDs (reuse if already assigned)
        import random as _rand
        unique_pids = list(dict.fromkeys(b["pid"] for b in blocks))
        for pid in unique_pids:
            if pid == "Idle":
                self.pid_colors[pid] = '#7f7f7f'
            elif pid not in self.pid_colors:
                self.pid_colors[pid] = '#%06x' % _rand.randint(0, 0xFFFFFF)

        # Draw flat blocks at y=0
        for b in blocks:
            duration = b["end"] - b["start"]
            color = self.pid_colors[b["pid"]]
            self.ax.barh(
                0, duration, left=b["start"], height=0.6,
                color=color, edgecolor='#1e1e1e', linewidth=1,
            )
            if duration >= 1:
                self.ax.text(
                    b["start"] + duration / 2, 0, b["pid"],
                    ha='center', va='center', color='white', fontsize=8, fontweight='bold',
                )

        self.ax.set_xlim(0, self.execution_log[-1]["time"] + 1 if self.execution_log else 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_yticks([])
        self.ax.set_title("Gantt Chart", color='white')

        # Build legend manually
        legend_elements = [Patch(facecolor=self.pid_colors[pid], label=pid) for pid in unique_pids]
        self.ax.legend(handles=legend_elements, loc='upper right', fontsize=7,
                       facecolor='#2b2b2b', edgecolor='white', labelcolor='white')

        self.canvas.draw()


if __name__ == "__main__":
    app = CPUSimulator()
    app.mainloop()
