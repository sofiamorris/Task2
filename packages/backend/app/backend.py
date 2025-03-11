import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class EnergyManager:
    def __init__(self, MWh_to_kg_conversion_factor=0.057, kg_to_MWh_conversion_factor=0.0336, hydrogen_sale_price=3):
        self.hydrogen_tank = 0.0  
        self.MWh_to_kg_hydrogen = MWh_to_kg_conversion_factor
        self.kg_to_MWh_hydrogen = kg_to_MWh_conversion_factor
        self.hydrogen_sale_price = hydrogen_sale_price  
        self.money_earned = 0.0
        self.money_saved = 0.0
        self.money_spent_tank = 0.0
        self.money_spent_notank = 0.0
        self.total_excess_energy = 0.0
        self.total_demand = 0.0
        self.max_hydrogen_tank_capacity = 15000
        # self.hydrogen_unable_to_store = 0


    def process_energy(self, timestamp, solar_generation, net_generation, demand, LMP, next_day_LMP):
        excess_energy = max(0, solar_generation - demand)
        deficit_energy = max(0, demand - solar_generation)
        print(timestamp)
        print(f"excess: {excess_energy}")
        print(f"demand: {demand}")
        self.total_excess_energy += excess_energy
        self.total_demand += demand

        if deficit_energy > 0:
            self.money_spent_notank += LMP * deficit_energy

        if excess_energy > 0:
            potential_hydrogen = excess_energy * self.MWh_to_kg_hydrogen
            
            hydrogen_to_store = min(potential_hydrogen, self.max_hydrogen_tank_capacity - self.hydrogen_tank)
            hydrogen_unable_to_store = potential_hydrogen - hydrogen_to_store
            self.hydrogen_tank = min(self.hydrogen_tank + hydrogen_to_store, self.max_hydrogen_tank_capacity)

            if hydrogen_unable_to_store > 0 and LMP > 0:
                energy_unable_to_store = hydrogen_unable_to_store * self.kg_to_MWh_hydrogen
                self.money_earned += energy_unable_to_store * LMP
                
            # # Sell hydrogen if profitable
            if self.hydrogen_sale_price * self.hydrogen_tank > LMP * (self.hydrogen_tank / self.kg_to_MWh_hydrogen):
                sell_amount = self.hydrogen_tank
                self.money_earned += sell_amount * self.hydrogen_sale_price
                self.hydrogen_tank -= sell_amount

        else:
            print("pulling from tank")
            hydrogen_needed = deficit_energy / self.kg_to_MWh_hydrogen
            hydrogen_used = min(hydrogen_needed, self.hydrogen_tank)

            self.hydrogen_tank -= hydrogen_used

            energy_provided = hydrogen_used * self.kg_to_MWh_hydrogen
            self.money_saved += abs(LMP) * energy_provided

            remaining_deficit = deficit_energy - energy_provided
            if remaining_deficit > 0:
                self.money_spent_tank += LMP * remaining_deficit 
                print(f"money spent: {LMP * remaining_deficit}")


        return {
            "timestamp": timestamp,
            "money_saved": self.money_saved,
            "money_earned": self.money_earned,
            "money_spent_tank": self.money_spent_tank,
            "hydrogen_tank": self.hydrogen_tank,
            "excess_energy": self.total_excess_energy,
            "demand": self.total_demand,
            "money_spent_notank": self.money_spent_notank,
        }


# Load real-time data
data = pd.read_csv("epe_merged_data.csv")
data = data.dropna(subset=['demand'])
# Ensure timestamps are in datetime format
data['timestamp'] = pd.to_datetime(data['timestamp'], format='%m/%d/%Y %H:%M:%S', errors='coerce')
# Drop rows where timestamp conversion failed (NaT values)
data = data.dropna(subset=['timestamp'])

# Sort data in ascending order (earliest date first)
data = data.sort_values(by='timestamp', ascending=True)

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
plt.plot(results_df["timestamp"], results_df["money_spent_tank"], label="Money Spent Using Storage", color="red")
plt.plot(results_df["timestamp"], results_df["money_spent_notank"], label="Money Spent Without Storage", color="blue")
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
results_df['demand'] = results_df['demand'].diff().fillna(results_df['demand'])
results_df['excess_energy'] = results_df['excess_energy'].diff().fillna(results_df['excess_energy'])


# Calculate daily averages
daily_averages = results_df.groupby('day').agg(
    average_demand=('demand', 'mean'),
    average_excess_energy=('excess_energy', 'mean'),
    average_energy_stored=('hydrogen_tank', 'mean'),
).reset_index()

# Calculate the average of the daily averages
average_of_daily_averages = daily_averages[['average_demand', 'average_excess_energy', 'average_energy_stored']].mean()

# Display the average of the daily averages
print("\n===== Average of Daily Averages =====")
print(f"Average Demand: {average_of_daily_averages['average_demand']:.2f} MWh")
print(f"Average Excess Energy: {average_of_daily_averages['average_excess_energy']:.2f} MWh")

# Final Summary
final_money_spent_tank = manager.money_spent_tank
final_money_spent_notank = manager.money_spent_notank
final_money_saved = manager.money_saved
final_money_earned = manager.money_earned

print("\n===== Final Summary =====")
print(f"Tank size: {manager.max_hydrogen_tank_capacity:.2f} kg")
print(f"Total Excess Energy: {manager.total_excess_energy:.2f} MWh")
print(f"Total Demand: {manager.total_demand:.2f} MWh")
print(f"Total Money Spent Using Storage: ${final_money_spent_tank:.2f}")
print(f"Total Money Spent Without Storage: ${final_money_spent_notank:.2f}")
print(f"Total Money Saved: ${final_money_saved:.2f}")
print(f"Total Money Earned: ${final_money_earned:.2f}")


plt.tight_layout()
plt.show()