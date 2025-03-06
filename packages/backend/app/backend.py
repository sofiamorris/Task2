import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class EnergyManager:
    def __init__(self, mWh_to_kg_conversion_factor=0.057, kg_to_mWh_conversion_factor=0.0336,
                 max_electrolyzer_power=10_000, max_fuel_cell_power=5_000, hydrogen_sale_price=3):
        self.hydrogen_tank = 0.0  
        self.mWh_to_kg_hydrogen = mWh_to_kg_conversion_factor
        self.kg_to_mWh_hydrogen = kg_to_mWh_conversion_factor
        self.max_electrolyzer_power = max_electrolyzer_power
        self.max_fuel_cell_power = max_fuel_cell_power
        self.hydrogen_sale_price = hydrogen_sale_price  
        self.money_saved = 0.0
        self.money_earned = 0.0
        self.money_spent = 0.0
        self.total_excess_energy = 0.0
        self.total_demand = 0.0
        self.max_hydrogen_tank_capacity = 15000

    def process_energy(self, timestamp, solar_generation, net_generation, demand, LMP, next_day_LMP):
        excess_energy = max(0, solar_generation - demand)
        deficit_energy = max(0, demand - solar_generation)

        # Track total energy
        self.total_excess_energy += excess_energy
        self.total_demand += demand

        if excess_energy > 0:
            if LMP <= 0:
                potential_hydrogen = excess_energy * self.mWh_to_kg_hydrogen
                
                # Ensure we do not exceed the tank capacity
                hydrogen_to_store = min(potential_hydrogen, self.max_electrolyzer_power, self.max_hydrogen_tank_capacity - self.hydrogen_tank)

                # Store in the hydrogen tank
                self.hydrogen_tank += hydrogen_to_store

                energy_stored_mWh = hydrogen_to_store * self.mWh_to_kg_hydrogen  # Convert back to mWh
            else:
                if next_day_LMP <= LMP:
                    self.money_earned += LMP * excess_energy

        else:
            hydrogen_needed = deficit_energy / self.kg_to_mWh_hydrogen
            hydrogen_used = min(hydrogen_needed, self.max_fuel_cell_power, self.hydrogen_tank)
            # print(f"hydrogen tank: {self.hydrogen_tank}")
            # print(f"max used: {max_hydrogen_used}")
            # print(f"hydrogen needed: {hydrogen_needed}")
            # print(f"hydrogen used: {hydrogen_used}")

            self.hydrogen_tank -= hydrogen_used
            energy_provided = hydrogen_used / self.kg_to_mWh_hydrogen
            self.money_saved += abs(LMP) * energy_provided

            remaining_deficit = deficit_energy - energy_provided
            
            if remaining_deficit > 0:
                if LMP < 50:  
                    self.money_spent += LMP * remaining_deficit 
                    # print(f"spending: {LMP * remaining_deficit}")

        
        # if self.hydrogen_sale_price * self.hydrogen_tank > LMP * (self.hydrogen_tank / self.kg_to_mWh_hydrogen):
        #     sell_amount = self.hydrogen_tank * 0.2  # Sell only 20% of the stored hydrogen
        #     self.money_earned += sell_amount * self.hydrogen_sale_price
        #     self.hydrogen_tank -= sell_amount

        
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
data = pd.read_csv("epe_merged_data.csv")
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