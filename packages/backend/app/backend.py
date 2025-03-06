import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class EnergyManager:
    def __init__(self, mWh_to_kg_conversion_factor=0.05, electrolyzer_efficiency=0.7, fuel_cell_efficiency=0.5,
                 max_electrolyzer_power=10_000, max_fuel_cell_power=5_000, hydrogen_sale_price=3):
        self.hydrogen_tank = 0.0  
        self.mWh_to_kg_hydrogen = mWh_to_kg_conversion_factor
        self.electrolyzer_efficiency = electrolyzer_efficiency
        self.fuel_cell_efficiency = fuel_cell_efficiency
        self.max_electrolyzer_power = max_electrolyzer_power
        self.max_fuel_cell_power = max_fuel_cell_power
        self.hydrogen_sale_price = hydrogen_sale_price  
        self.money_saved = 0.0
        self.money_earned = 0.0
        self.money_spent = 0.0
        self.total_excess_energy = 0.0
        self.total_demand = 0.0
        self.max_hydrogen_tank_capacity = 112500

    def process_energy(self, timestamp, solar_generation, net_generation, demand, LMP, next_day_LMP):
        excess_energy = max(0, solar_generation - demand)
        deficit_energy = max(0, demand - solar_generation)

        # Track total energy
        self.total_excess_energy += excess_energy
        self.total_demand += demand

        if excess_energy > 0:
            if LMP <= 0:
                max_hydrogen_to_store = (self.max_electrolyzer_power * self.electrolyzer_efficiency) / self.mWh_to_kg_hydrogen
                potential_hydrogen = (excess_energy * self.electrolyzer_efficiency) / self.mWh_to_kg_hydrogen
                
                # Ensure we do not exceed the tank capacity
                hydrogen_to_store = min(potential_hydrogen, max_hydrogen_to_store, self.max_hydrogen_tank_capacity - self.hydrogen_tank)

                # Store in the hydrogen tank
                self.hydrogen_tank += hydrogen_to_store

                energy_stored_mWh = hydrogen_to_store * self.mWh_to_kg_hydrogen  # Convert back to mWh
                self.money_saved += abs(LMP) * energy_stored_mWh
            else:
                if next_day_LMP <= LMP:
                    self.money_earned += LMP * excess_energy

        else:
            max_hydrogen_used = (self.max_fuel_cell_power / self.mWh_to_kg_hydrogen) / self.fuel_cell_efficiency
            hydrogen_needed = deficit_energy / (self.mWh_to_kg_hydrogen * self.fuel_cell_efficiency)
            hydrogen_used = min(hydrogen_needed, max_hydrogen_used, self.hydrogen_tank)
            self.hydrogen_tank -= hydrogen_used
            energy_provided = hydrogen_used * self.mWh_to_kg_hydrogen * self.fuel_cell_efficiency
            remaining_deficit = deficit_energy - energy_provided
            
            if remaining_deficit > 0:
                if LMP < 50:  
                    self.money_spent += LMP * remaining_deficit 
        
        if self.hydrogen_sale_price * self.hydrogen_tank > LMP * (self.hydrogen_tank * self.mWh_to_kg_hydrogen * self.fuel_cell_efficiency):
            sell_amount = self.hydrogen_tank * 0.2  # Sell only 20% of the stored hydrogen
            self.money_earned += sell_amount * self.hydrogen_sale_price
            self.hydrogen_tank -= sell_amount

        
        net_energy_revenue = self.money_earned + self.money_saved - self.money_spent
        
        return {
            "timestamp": timestamp,
            "money_saved": self.money_saved,
            "money_earned": self.money_earned,
            "money_spent": self.money_spent,
            "net_energy_revenue": net_energy_revenue,
            "hydrogen_tank": self.hydrogen_tank,
            "excess_energy": self.total_excess_energy,
            "demand": self.total_demand
        }

# Load real-time data
data = pd.read_csv("iid_merged_data.csv")
data = data.dropna(subset=['demand'])

manager = EnergyManager()

results = []
for i, row in data.iterrows():
    next_day_LMP = data.iloc[i+1]["LMP"] if i < len(data)-1 else row["LMP"]  
    result = manager.process_energy(
        row["timestamp"], row["solar_generation"], row["net_generation"], row["demand"], row["LMP"], next_day_LMP
    )
    results.append(result)

results_df = pd.DataFrame(results)

# Plot results
plt.figure(figsize=(10, 5))
plt.plot(results_df["timestamp"], results_df["money_saved"], label="Money Saved", color="green")
plt.plot(results_df["timestamp"], results_df["money_earned"], label="Money Earned", color="blue")
plt.plot(results_df["timestamp"], results_df["money_spent"], label="Money Spent", color="red")
plt.plot(results_df["timestamp"], results_df["net_energy_revenue"], label="Net Energy Revenue", color="purple", linestyle="--")
plt.xlabel("Timestamp")
plt.ylabel("Dollars ($)")
plt.title("Financial Impact of Hydrogen Storage System")
plt.legend()

# Show fewer x-axis labels
tick_positions = np.linspace(0, len(results_df["timestamp"]) - 1, num=10, dtype=int)  # Pick 10 evenly spaced ticks
plt.xticks(results_df["timestamp"].iloc[tick_positions], rotation=45)


# Convert the 'timestamp' to datetime with the correct format and handle missing seconds
results_df['timestamp'] = pd.to_datetime(results_df['timestamp'], format='%m/%d/%Y %H:%M:%S', errors='coerce')

# Extract date for grouping
results_df['day'] = results_df['timestamp'].dt.date  # Extracting only the date

# Calculate daily averages
daily_averages = results_df.groupby('day').agg(
    average_demand=('demand', 'mean'),
    average_excess_energy=('excess_energy', 'mean'),
    average_energy_stored=('hydrogen_tank', 'mean'),
    average_money_saved=('money_saved', 'mean')
).reset_index()

# Calculate the average of the daily averages
average_of_daily_averages = daily_averages[['average_demand', 'average_excess_energy', 'average_energy_stored', 'average_money_saved']].mean()

# Display the average of the daily averages
print("\n===== Average of Daily Averages =====")
print(f"Average Demand: {average_of_daily_averages['average_demand']:.2f} mWh")
print(f"Average Excess Energy: {average_of_daily_averages['average_excess_energy']:.2f} mWh")
# print(f"Average Energy Stored: {average_of_daily_averages['average_energy_stored']:.2f} mWh")
print(f"Average Money Saved: ${average_of_daily_averages['average_money_saved']:.2f}")

# Final Summary
final_money_earned = manager.money_earned
final_money_spent = manager.money_spent
final_money_saved = manager.money_saved
final_net_revenue = final_money_earned + final_money_saved - final_money_spent

# Final Summary
final_money_earned = manager.money_earned
final_money_spent = manager.money_spent
final_money_saved = manager.money_saved
final_net_revenue = final_money_earned + final_money_saved - final_money_spent

print("\n===== Final Summary =====")
print(f"Tank size: {manager.max_hydrogen_tank_capacity:.2f} kg")
print(f"Total Excess Energy: {manager.total_excess_energy:.2f} mWh")
print(f"Total Demand: {manager.total_demand:.2f} mWh")
print(f"Total Money Earned: ${final_money_earned:.2f}")
print(f"Total Money Spent: ${final_money_spent:.2f}")
print(f"Total Money Saved: ${final_money_saved:.2f}")
print(f"Final Net Revenue: ${final_net_revenue:.2f}")


plt.tight_layout()
plt.show()