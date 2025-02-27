"""MIT License

Copyright (c) 2025 Hamza Ozdemir tr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import os

# Initial values
battery_capacity = 14000  # mAh
current_usage = 0
save_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "device_data.json")  # Save JSON file in the same folder

def save_data():
    """Saves the list to a JSON file."""
    devices = device_list.get(0, tk.END)
    with open(save_file, "w") as f:
        json.dump(list(devices), f)

def load_data():
    """Loads the device list from a JSON file."""
    global current_usage
    if os.path.exists(save_file):
        with open(save_file, "r") as f:
            devices = json.load(f)
            for device in devices:
                device_list.insert(tk.END, device)
                parts = device.split('|')
                consumption_part = parts[-1].strip().split(': ')[1]
                current_usage += float(consumption_part.split()[0])
        update_progress_bar()

def add_device():
    global current_usage
    name = name_entry.get().strip()
    try:
        current = float(current_entry.get()) / 1e6  # uA to A conversion
        time = float(time_entry.get()) / 3600  # Convert from seconds to hours
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number!")
        return
    
    consumption = current * time * 1000  # Consumption in mAh
    current_usage += consumption
    
    if not name:
        name = "Unknown Device"
    
    # Add to list
    device_list.insert(tk.END, f"{name} | Current: {current * 1e6:.2f} uA | Duration: {time * 3600:.0f} s | Consumption: {consumption:.6f} mAh")
    
    update_progress_bar()
    save_data()
    
    if current_usage > battery_capacity:
        messagebox.showwarning("Warning", "Battery capacity exceeded!")
    
    name_entry.delete(0, tk.END)
    current_entry.delete(0, tk.END)
    time_entry.delete(0, tk.END)

def update_progress_bar():
    ax.clear()
    ax.barh(["Battery Usage"], [current_usage], color='green')
    ax.set_xlim(0, battery_capacity)
    ax.set_xlabel("mAh")
    
    ax.text(battery_capacity * 1.02, 0, f"{current_usage:.2f} mAh", va='center', fontsize=10, color='black')
    ax.set_xticks(range(0, battery_capacity+1, 1000))  
    
    canvas.draw()

def reset_all():
    global current_usage
    current_usage = 0
    device_list.delete(0, tk.END)
    if os.path.exists(save_file):
        os.remove(save_file)
    update_progress_bar()

def on_resize(event):
    fig.set_size_inches(event.width / 100, 1)
    canvas.draw()

# Tkinter GUI
root = tk.Tk()
root.title("Current Consumption Calculator")
root.bind("<Configure>", on_resize)

frame = tk.Frame(root)
frame.pack(pady=10)

# Input fields
tk.Label(frame, text="Device Name:").grid(row=0, column=0)
name_entry = tk.Entry(frame)
name_entry.grid(row=0, column=1)

tk.Label(frame, text="Current (uA)(value only):").grid(row=1, column=0)
current_entry = tk.Entry(frame)
current_entry.grid(row=1, column=1)

tk.Label(frame, text="Run Time (sec):").grid(row=2, column=0)
time_entry = tk.Entry(frame)
time_entry.grid(row=2, column=1)

tk.Button(frame, text="Add", command=add_device).grid(row=3, column=0)
tk.Button(frame, text="Reset", command=reset_all).grid(row=3, column=1)

# List box
device_list = tk.Listbox(root, width=60)
device_list.pack(pady=10, fill=tk.BOTH, expand=True)

# Matplotlib for Progress Bar
fig, ax = plt.subplots(figsize=(5, 1))
ax.set_xlim(0, battery_capacity)
ax.barh(["Battery Usage"], [0], color='green')
ax.set_xlabel("mAh")
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.X)

# Load previous data
load_data()

root.mainloop()

# Thanks to GPT @veyqhud