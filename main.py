import random
import tkinter as tk
from tkinter import ttk

class Process:
    def __init__(self, pid, arrival_time, burst_time):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.waiting_time = 0
        self.completion_time = 0
        self.turnaround_time = 0

def fcfs(processes):
    processes.sort(key=lambda x: x.arrival_time)
    time = 0
    total_waiting_time = 0

    for process in processes:
        if time < process.arrival_time:
            time = process.arrival_time
        process.waiting_time = time - process.arrival_time
        process.completion_time = time + process.burst_time
        total_waiting_time += process.waiting_time
        time += process.burst_time

    return total_waiting_time / len(processes)

def sjf_non_preemptive(processes):
    processes.sort(key=lambda x: (x.arrival_time, x.burst_time))
    time = 0
    total_waiting_time = 0
    remaining = processes[:]

    while remaining:
        available = [p for p in remaining if p.arrival_time <= time]
        if available:
            process = min(available, key=lambda x: x.burst_time)
            remaining.remove(process)
            process.waiting_time = time - process.arrival_time
            process.completion_time = time + process.burst_time
            total_waiting_time += process.waiting_time
            time += process.burst_time
        else:
            time += 1

    return total_waiting_time / len(processes)

def sjf_preemptive(processes):
    time = 0
    total_waiting_time = 0
    remaining = processes[:]
    ready_queue = []
    completed = 0

    while completed < len(processes):
        ready_queue.extend([p for p in remaining if p.arrival_time <= time])
        remaining = [p for p in remaining if p not in ready_queue]

        if ready_queue:
            ready_queue.sort(key=lambda x: x.remaining_time)
            current_process = ready_queue[0]

            time += 1
            current_process.remaining_time -= 1

            if current_process.remaining_time == 0:
                current_process.completion_time = time
                current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
                current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
                total_waiting_time += current_process.waiting_time
                ready_queue.remove(current_process)
                completed += 1
        else:
            time += 1

    return total_waiting_time / len(processes)

def round_robin(processes, quantum):
    queue = sorted(processes, key=lambda x: x.arrival_time)
    time = 0
    total_waiting_time = 0
    n = len(processes)

    while queue:
        process = queue.pop(0)
        if time < process.arrival_time:
            time = process.arrival_time

        process.waiting_time += time - process.arrival_time

        if process.remaining_time > quantum:
            time += quantum
            process.remaining_time -= quantum
            queue.append(process)
        else:
            time += process.remaining_time
            process.remaining_time = 0

    total_waiting_time = sum(p.waiting_time for p in processes)
    return total_waiting_time / n

def generate_processes(num_processes):
    return [Process(i, random.randint(0, 10), random.randint(1, 10)) for i in range(num_processes)]

def run_simulation():
    user_quantum = int(entry_quantum.get())
    batch_count = int(entry_batches.get())
    num_processes = int(entry_num_processes.get())

    fcfs_total, sjf_NP_total, sjf_P_total, rr_total = 0, 0, 0, 0
    batch_results = []

    for batch in range(batch_count):
        processes = generate_processes(num_processes)
       
        fcfs_processes = [Process(p.pid, p.arrival_time, p.burst_time) for p in processes]
        sjf_NP_processes = [Process(p.pid, p.arrival_time, p.burst_time) for p in processes]
        sjf_P_processes = [Process(p.pid, p.arrival_time, p.burst_time) for p in processes]
        rr_processes = [Process(p.pid, p.arrival_time, p.burst_time) for p in processes]


        max_burst_time = max(p.burst_time for p in processes)
        quantum = max_burst_time if user_quantum == -1 else user_quantum

        fcfs_avg = fcfs(fcfs_processes)
        sjf_NP_avg = sjf_non_preemptive(sjf_NP_processes)
        sjf_P_avg = sjf_preemptive(sjf_P_processes)
        rr_avg = round_robin(rr_processes, quantum)

        fcfs_total += fcfs_avg
        sjf_NP_total += sjf_NP_avg
        sjf_P_total += sjf_P_avg
        rr_total += rr_avg
        batch_results.append((batch + 1, fcfs_avg, sjf_NP_avg, sjf_P_avg, rr_avg, quantum))

    avg_fcfs = fcfs_total / batch_count
    avg_sjf_NP = sjf_NP_total / batch_count
    avg_sjf_P = sjf_P_total / batch_count
    avg_rr = rr_total / batch_count
    overall_avg = (avg_fcfs + avg_sjf_NP + avg_sjf_P + avg_rr) / 4

    result_label.config(
        text=f"FCFS: {avg_fcfs:.2f}\nSJF(NP): {avg_sjf_NP:.2f}\nSJF(P): {avg_sjf_P:.2f}\nRound Robin: {avg_rr:.2f}\n\nAverage Waiting Time: {overall_avg:.2f}\n")

    for i in tree.get_children():
        tree.delete(i)

    for batch in batch_results:
        tree.insert("", "end", values=batch)

    tree.update_idletasks()

root = tk.Tk()
root.title("CPU Scheduling Simulator")
root.geometry("800x400")

frame = tk.Frame(root)
frame.pack()

settings_frame = tk.Frame(frame)
settings_frame.pack(side=tk.LEFT, padx=10, pady=10)

entry_quantum = tk.Entry(settings_frame, width=5)
entry_quantum.insert(0, "-1")
entry_batches = tk.Entry(settings_frame, width=5)
entry_batches.insert(0, "10")
entry_num_processes = tk.Entry(settings_frame, width=5)
entry_num_processes.insert(0, "5")

entries = [("Quantum (-1 for max)", entry_quantum), ("Batches", entry_batches), ("Processes", entry_num_processes)]
for i, (label, entry) in enumerate(entries):
    tk.Label(settings_frame, text=label).grid(row=i, column=0)
    entry.grid(row=i, column=1)

run_button = tk.Button(settings_frame, text="Run Simulation", command=run_simulation)
run_button.grid(row=len(entries), column=0, columnspan=2, pady=5)

result_label = tk.Label(frame, text="", justify=tk.LEFT)
result_label.pack()

columns = ("Batch", "FCFS", "SJF(NP)", "SJF(P)", "RR", "Quantum")
tree = ttk.Treeview(frame, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)
tree.pack()

root.mainloop()
