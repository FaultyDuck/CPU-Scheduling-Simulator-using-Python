import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import randomGen
import FCFS
import PriorityScheduling

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class CPUSimulator(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("CPU Scheduling Simulator")
        self.geometry("900x600")
        
        self.processes = [] #list to store processes generated
        self.execution_log = [] #list to store execution log
        self.current_time = 0
        self.is_simulating = False
        
        self.setup_ui_layout()
        self.setup_matplotlib_chart()

    def setup_ui_layout(self):
        # Top Header / Control Panel
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.pack(fill="x", padx=20, pady=10)
        
        self.btn_generate = ctk.CTkButton(self.control_frame, text="Generate Data", command=self.on_generate, text_color="Black") #calls generate function
        self.btn_generate.pack(side="left", padx=10, pady=10)
        
        self.btn_start = ctk.CTkButton(self.control_frame, text="Start Simulation", command=self.on_start, state="disabled", text_color="Black") #calls the start function
        self.btn_start.pack(side="left", padx=10, pady=10)
        
        self.topRightStatus = ctk.CTkLabel(self.control_frame, text="Status: Awaiting Data") #top right status updates
        self.topRightStatus.pack(side="right", padx=20)

        # Bottom Area: Split into Table View and Gantt Chart View
        self.display_frame = ctk.CTkFrame(self)
        self.display_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side textbox to print raw metrics/data logs
        self.txt_log = ctk.CTkTextbox(self.display_frame, width=250)
        self.txt_log.pack(side="left", fill="y", padx=10, pady=10)
        self.txt_log.insert("0.0", "Process Table:\nClick 'Generate Data' to begin.")

    def setup_matplotlib_chart(self):
        # Create a Matplotlib figure that matches dark mode stylings
        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.fig.patch.set_facecolor('#2b2b2b') # Matches CTk Frame background roughly
        self.ax.set_facecolor('#1e1e1e')
        self.ax.tick_params(colors='white')
        self.ax.set_title("Gantt Chart Real-Time Visualizer", color='white')
        
        # Embed the plot window into CustomTkinter window structure
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.display_frame)
        self.canvas.get_tk_widget().pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def on_generate(self): #checking to generate the data
        self.processes = randomGen.generate_random_processes(5) #generates 5 processes from scheduler
        self.execution_log = []
        self.current_time = 0
        
        #Print processes to textbox
        self.txt_log.delete("0.0", "end")
        self.txt_log.insert("0.0", "PID\tArrival\tBurst\tPriority\n" + "-"*50 + "\n")
        for p in self.processes:
            self.txt_log.insert("end", f"{p['pid']}\t{p['arrival_time']}\t{p['burst_time']}\t{p['priority']}\n") #format to print
            
        self.topRightStatus.configure(text="Status: Data Loaded ready to Run")
        self.btn_start.configure(state="normal") #enable start button
        self.redraw_gantt_chart()

    def on_start(self):
        if not self.is_simulating and self.processes:
            self.is_simulating = True
            self.btn_start.configure(state="disabled")
            self.btn_generate.configure(state="disabled")
            self.simulation_loop_tick()

    def simulation_loop_tick(self):
        if not self.is_simulating:
            return
        #not yet put a picker for user to switch between which algorithm
        finished = PriorityScheduling.priorityScheduling(self.processes, self.current_time, self.execution_log)
        #Log to the top right textbox what is running right now
        current_tick_job = self.execution_log[-1]["pid"]
        self.topRightStatus.configure(text=f"Time: {self.current_time}ms | Active: {current_tick_job}")
        
        self.redraw_gantt_chart()
        
        self.current_time += 1
        
        if finished:
            self.is_simulating = False
            self.topRightStatus.configure(text=f"Simulation Complete at {self.current_time}ms!")
            self.btn_generate.configure(state="normal")
        else:
            self.after(100, self.simulation_loop_tick)

    def redraw_gantt_chart(self): #idk how this works yet
        self.ax.clear()
        self.ax.set_facecolor('#1e1e1e')
        self.ax.tick_params(colors='white')
        self.ax.set_xlabel("Time Units", color='white')
        self.ax.set_ylabel("Processes", color='white')
        
        # Process logs to structure Matplotlib broken_barh data
        # broken_barh requires formats: [(start_time, duration)], (y_position, height)
        pid_positions = {}
        unique_pids = list(set([item["pid"] for item in self.execution_log]))
        
        for index, pid in enumerate(unique_pids):
            pid_positions[pid] = (index * 10 + 5, 8) # ypos, thickness
            
        # Draw blocks based on accumulated logged ticks
        for entry in self.execution_log:
            time_start = entry["time"]
            pid = entry["pid"]
            y_config = pid_positions[pid]
            
            # Draw individual block piece
            self.ax.broken_barh([(time_start, 1)], y_config, facecolors=('#1f77b4' if pid != "Idle" else '#7f7f7f'))

        # Set custom labels on the Y-axis to see process IDs clearly
        self.ax.set_yticks([pos[0] + 4 for pos in pid_positions.values()])
        self.ax.set_yticklabels(pid_positions.keys())
        
        self.canvas.draw()

if __name__ == "__main__":
    app = CPUSimulator()
    app.mainloop()