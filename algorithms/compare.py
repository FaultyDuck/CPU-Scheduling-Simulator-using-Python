import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Patch
from copy import deepcopy

from . import RR, SJF


class Comparison:
    def __init__(self, parent):
        self.parent = parent

    def run_algorithm_simulation(self, algo_name, processes):
        """Run a simulation of the given algorithm and return the resulting process states and execution log.

        Deep copies the original processes to avoid mutation, then iterates
        tick-by-tick using the selected algorithm until all processes finish.
        """
        procs = deepcopy(processes)
        for p in procs:
            p["remaining_time"] = 0
            p["completed"] = False
            p["completion_time"] = 0

        exec_log = []
        current_time = 0

        if algo_name == "Round Robin (RR)":
            algo = RR.RR(quantum=int(self.parent.quantum_var.get()))
            algo_fn = algo.run_tick
        elif algo_name == "Shortest Job First (SJF)":
            algo = SJF.SJF(preemptive=self.parent.preemptive_var.get())
            algo_fn = algo.run_tick
        else:
            algo_fn = self.parent.algorithms[algo_name]

        finished = False
        while not finished:
            finished = algo_fn(procs, current_time, exec_log)
            current_time += 1

        return procs, exec_log

    def show_comparison(self):
        """Build and display the comparison window with metrics tables and Gantt charts for each algorithm."""
        if not self.parent.processes:
            return

        # Build a consistent color palette keyed by PID
        all_pids = list(dict.fromkeys(p["pid"] for p in self.parent.processes))
        palette = {}
        for i, pid in enumerate(all_pids):
            palette[pid] = plt.cm.Set2(i / max(len(all_pids), 1))

        # Run every registered algorithm and collect per-process metrics
        results = {}
        for algo_name in self.parent.algorithms:
            procs, exec_log = self.run_algorithm_simulation(algo_name, self.parent.processes)

            # Determine each process's completion time from the last execution log entry
            for p in procs:
                p["completion_time"] = 0
            for entry in reversed(exec_log):
                pid = entry["pid"]
                if pid == "Idle":
                    continue
                for p in procs:
                    if p["pid"] == pid and p["completion_time"] == 0:
                        p["completion_time"] = entry["time"] + 1

            # Calculate Turnaround Time (TAT) and Waiting Time (WT) for each process
            total_tat = 0
            total_wt = 0
            process_metrics = []
            for p in procs:
                ct = p["completion_time"]
                tat = ct - p["arrival_time"]
                wt = tat - p["burst_time"]
                total_tat += tat
                total_wt += wt
                process_metrics.append({
                    "pid": p["pid"],
                    "arrival_time": p["arrival_time"],
                    "burst_time": p["burst_time"],
                    "priority": p.get("priority", 0),
                    "completion_time": ct,
                    "tat": tat,
                    "wt": wt,
                })

            n = len(procs)
            results[algo_name] = {
                "processes": process_metrics,
                "avg_tat": total_tat / n if n else 0,
                "avg_wt": total_wt / n if n else 0,
                "exec_log": exec_log,
            }

        # --- Comparison Window Setup ---
        win = ctk.CTkToplevel(self.parent)
        win.title("Algorithm Comparison")
        win.geometry("900x900")
        win.configure(fg_color="#2b2b2b")

        scroll = ctk.CTkScrollbar(win, orientation="vertical")
        scroll.pack(side="right", fill="y")

        canvas = ctk.CTkCanvas(win, bg="#2b2b2b", highlightthickness=0,
                               yscrollcommand=scroll.set)
        scroll.configure(command=canvas.yview)

        inner = ctk.CTkFrame(canvas, fg_color="#2b2b2b")
        canvas_window = canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.pack(side="left", fill="both", expand=True)

        # Resize inner frame to match canvas width for proper horizontal layout
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        inner.bind("<Configure>", on_frame_configure)

        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)

        # Cross-platform scroll bindings (mousewheel for Windows/Mac, buttons 4/5 for Linux)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        def _on_button_4(event):
            canvas.yview_scroll(-1, "units")
        def _on_button_5(event):
            canvas.yview_scroll(1, "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", _on_button_4)
        canvas.bind_all("<Button-5>", _on_button_5)

        # Title
        ctk.CTkLabel(inner, text="Algorithm Comparison",
                      font=ctk.CTkFont(size=20, weight="bold"),
                      text_color="white").pack(pady=(10, 5))

        # Summary of input processes
        proc_text = "Processes: " + ", ".join(
            f"{p['pid']}(AT={p['arrival_time']}, BT={p['burst_time']}, PRI={p.get('priority', 0)})"
            for p in self.parent.processes
        )
        ctk.CTkLabel(inner, text=proc_text, text_color="#aaaaaa",
                      font=ctk.CTkFont(size=11)).pack(pady=(0, 10))

        # Per algorithm, draw metrics table and Gantt chart
        for algo_name, data in results.items():
            ctk.CTkLabel(inner, text=f"--- {algo_name} ---",
                          font=ctk.CTkFont(size=16, weight="bold"),
                          text_color="#4fc3f7").pack(pady=(15, 5))

            # Metrics table (PID, AT, BT, CT, TAT, WT)
            table = ctk.CTkFrame(inner, fg_color="#333333")
            table.pack(fill="x", padx=20, pady=5)

            headers = ["PID", "AT", "BT", "PRI", "CT", "TAT", "WT"]
            for i, h in enumerate(headers):
                ctk.CTkLabel(table, text=h, font=ctk.CTkFont(weight="bold"),
                              text_color="white", width=70).grid(row=0, column=i, padx=3, pady=3)

            for r, proc in enumerate(data["processes"], 1):
                vals = [proc["pid"], proc["arrival_time"], proc["burst_time"],
                        proc["priority"], proc["completion_time"], proc["tat"], proc["wt"]]
                for c, v in enumerate(vals):
                    ctk.CTkLabel(table, text=str(v), text_color="white",
                                  width=70).grid(row=r, column=c, padx=3, pady=2)

            # Average TAT and WT summary line
            avg_text = f"Average TAT: {data['avg_tat']:.2f}   |   Average WT: {data['avg_wt']:.2f}"
            ctk.CTkLabel(inner, text=avg_text, text_color="#81c784",
                          font=ctk.CTkFont(size=13)).pack(pady=5)

            # Gantt Chart
            fig, ax = plt.subplots(figsize=(8, 1.8))
            fig.patch.set_facecolor('#2b2b2b')
            ax.set_facecolor('#1e1e1e')
            ax.tick_params(colors='white', labelsize=7)

            # Merge consecutive same-PID entries into contiguous blocks
            blocks = []
            for entry in data["exec_log"]:
                pid = entry["pid"]
                t = entry["time"]
                if blocks and blocks[-1]["pid"] == pid:
                    blocks[-1]["end"] = t + 1
                else:
                    blocks.append({"pid": pid, "start": t, "end": t + 1})

            # Map each PID to a display color
            unique_pids = list(dict.fromkeys(b["pid"] for b in blocks))
            colors = {}
            for pid in unique_pids:
                if pid == "Idle":
                    colors[pid] = '#7f7f7f'
                else:
                    r, g, b, _ = palette[pid]
                    colors[pid] = '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))

            # Draw horizontal bars for each block
            for b in blocks:
                duration = b["end"] - b["start"]
                ax.barh(0, duration, left=b["start"], height=0.6,
                        color=colors[b["pid"]], edgecolor='#1e1e1e', linewidth=1)
                if duration >= 1:
                    ax.text(b["start"] + duration / 2, 0, b["pid"],
                            ha='center', va='center', color='white',
                            fontsize=7, fontweight='bold')

            ax.set_xlim(0, data["exec_log"][-1]["time"] + 1 if data["exec_log"] else 1)
            ax.set_ylim(-1, 1)
            ax.set_yticks([])
            ax.set_xlabel("Time Units", color='white', fontsize=7)
            ax.set_title(f"{algo_name} - Gantt Chart", color='white', fontsize=9)

            legend_elements = [Patch(facecolor=colors[pid], label=pid) for pid in unique_pids]
            ax.legend(handles=legend_elements, loc='upper right', fontsize=6,
                      facecolor='#2b2b2b', edgecolor='white', labelcolor='white')

            fig.tight_layout(pad=0.5)
            gantt_canvas = FigureCanvasTkAgg(fig, master=inner)
            gantt_canvas.get_tk_widget().pack(fill="x", padx=20, pady=5)
            gantt_canvas.draw()
            plt.close(fig)

        # Overall Comparison Summary Table
        ctk.CTkLabel(inner, text="--- Overall Comparison ---",
                      font=ctk.CTkFont(size=16, weight="bold"),
                      text_color="#ffb74d").pack(pady=(20, 5))

        summary = ctk.CTkFrame(inner, fg_color="#333333")
        summary.pack(fill="x", padx=20, pady=5)

        for i, h in enumerate(["Algorithm", "Avg TAT", "Avg WT"]):
            ctk.CTkLabel(summary, text=h, font=ctk.CTkFont(weight="bold"),
                          text_color="white", width=180).grid(row=0, column=i, padx=5, pady=5)

        for r, (name, data) in enumerate(results.items(), 1):
            ctk.CTkLabel(summary, text=name, text_color="white",
                          width=180).grid(row=r, column=0, padx=5, pady=3)
            ctk.CTkLabel(summary, text=f"{data['avg_tat']:.2f}", text_color="white",
                          width=180).grid(row=r, column=1, padx=5, pady=3)
            ctk.CTkLabel(summary, text=f"{data['avg_wt']:.2f}", text_color="white",
                          width=180).grid(row=r, column=2, padx=5, pady=3)