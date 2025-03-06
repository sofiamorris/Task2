# gui.py
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from backend import EnergyManager
import pandas as pd

# Initialize the main window
window = tk.Tk()
window.title("Energy Management Interface")
window.geometry("800x500")  # Adjusted for graphs
window.configure(bg="#e8e8e8")  # Light gray background

# Create an instance of EnergyManager
energy_manager = EnergyManager(50)

# Lists to store data for plotting
time_steps = []
power_needed_data = []
power_generated_data = []
hydrogen_tank_data = []
firmed_energy_output_data = []
time_counter = 0

# Function to update the UI and data for graphs
# Function to update the UI and data for graphs
def update_energy_flow():
    global time_counter

    df = pd.read_csv("merged_data.csv", parse_dates=["timestamp"])

    # Simulate real-time updates
    for _, row in df.iterrows():
        timestamp = row["timestamp"]
        solar_generation = row["solar_generation"]
        net_generation = row["net_generation"]
        demand = row["demand"]
        lmp = row["LMP"]

        # Process data using the EnergyManager
        energy_manager.process_data(timestamp, solar_generation, net_generation, demand, lmp)

        # Append time step and data for plotting
        time_steps.append(timestamp)
        power_needed_data.append(demand)  # Use actual demand value
        power_generated_data.append(solar_generation)  # Use actual solar generation
        hydrogen_tank_data.append(energy_manager.hydrogen_tank)
        firmed_energy_output_data.append(energy_manager.firmed_energy)

    # Update result text and money display
    result.set(energy_manager.result)
    savings_label.config(text=f"Money Saved: ${energy_manager.money_saved:.2f}")
    earnings_label.config(text=f"Money Earned: ${energy_manager.money_earned:.2f}")

    # Update graphs
    time_counter += 1
    update_graphs()


# Function to update the graphs
def update_graphs():
    title_font_size = "8"
    axis_title_font_size = "6"
    legend_font_size = "6"
    ax1.clear()
    ax1.plot(time_steps, power_needed_data, label="Power Needed", color="red")
    ax1.plot(time_steps, power_generated_data, label="Power Generated", color="green")
    ax1.set_title("Power Needed vs. Power Generated", fontsize=title_font_size)
    ax1.set_xlabel("Time", fontsize=axis_title_font_size)
    ax1.set_ylabel("Power (kWh)", fontsize=axis_title_font_size)
    ax1.legend(fontsize=legend_font_size)
    
    ax2.clear()
    ax2.plot(time_steps, hydrogen_tank_data, label="Hydrogen Tank Level", color="blue")
    ax2.set_title("Hydrogen Tank Over Time", fontsize=title_font_size)
    ax2.set_xlabel("Time", fontsize=axis_title_font_size)
    ax2.set_ylabel("Tank Level (kg)", fontsize=axis_title_font_size)
    ax2.legend(fontsize=legend_font_size)

    ax3.clear()
    ax3.plot(time_steps, firmed_energy_output_data, label="Firmed Energy Output", color="yellow")
    ax3.set_title("Firmed Energy Output Over Time", fontsize=title_font_size)
    ax3.set_xlabel("Time", fontsize=axis_title_font_size)
    ax3.set_ylabel("Power (kWh)", fontsize=axis_title_font_size)
    ax3.legend(fontsize=legend_font_size)

    canvas.draw()

# Create labels for Power Needed, Power Generated, and Conversion Rate
slider_frame = tk.Frame(window, bg="#e8e8e8")
slider_frame.pack(pady=20, side=tk.LEFT, padx=20)

# kWh to hydrogen (kg) Conversion Factor Text Entry
label_conversion = tk.Label(slider_frame, text="Conversion Rate: kWh to kg of hydrogen", 
                        font=("Arial", 12), bg="#e8e8e8", fg="black")
label_conversion.pack(pady=5)
conversion_entry = tk.Entry(slider_frame, width=30)  # width sets the visible width in characters
conversion_entry.pack(pady=5)  # Add the entry to the window
conversion_entry.insert(0, f"{energy_manager.kWh_to_kg_hydrogen}")  # default value

# Button to get entry data
get_button = ttk.Button(slider_frame, text="Update Values", command=lambda: update_values())
get_button.pack(pady=10)

# Label to display the result
result = tk.StringVar()
result_label = tk.Label(slider_frame, textvariable=result, font=("Arial", 12), 
                        bg="#e8e8e8", fg="black", justify="left", wraplength=250)
result_label.pack(pady=10)

# Label to display savings
savings_label = tk.Label(slider_frame, text="Money Saved: $0.00", font=("Arial", 12), bg="#e8e8e8", fg="black")
savings_label.pack(pady=5)

# Label to display earnings
earnings_label = tk.Label(slider_frame, text="Money Earned: $0.00", font=("Arial", 12), bg="#e8e8e8", fg="black")
earnings_label.pack(pady=5)

# Matplotlib Figure and Axes
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(5, 6))
fig.tight_layout(pad=4)

canvas = FigureCanvasTkAgg(fig, master=window)
canvas.get_tk_widget().pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

# Function to repeatedly call update_energy_flow on a timer
def auto_update_energy_flow():
    update_energy_flow()
    window.after(1000, auto_update_energy_flow)  # Update every second

# Start the recurring updates
auto_update_energy_flow()

# Run the main loop
window.mainloop()