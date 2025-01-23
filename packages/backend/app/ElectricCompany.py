import random

class ElectricCompany:
    def __init__(self):
        self.grid_demand = random.uniform(50, 100)  # MW
        self.grid_supply = random.uniform(50, 100)  # MW
        self.market_price = random.uniform(-20, 100)  # Simulate market price, can go negative

    def monitor_grid(self):
        """Check the current grid state."""
        print(f"[Grid] Market Price: ${self.market_price:.2f}/MWh | Demand: {self.grid_demand:.2f} MW | Supply: {self.grid_supply:.2f} MW")
        return self.grid_demand - self.grid_supply, self.market_price

    def send_to_hydrogen_storage(self, excess_power, hydrogen_storage_company):
        """Send excess energy to hydrogen storage when market price is negative."""
        if self.market_price < 0 and excess_power > 0:
            # Convert excess power to kWh (assume 1 MW = 1000 kW)
            kWh_to_store = min(excess_power * 1000, hydrogen_storage_company.available_capacity())
            hydrogen_storage_company.store_energy(kWh_to_store)
            print(f"[Grid] Sent {kWh_to_store} kWh to hydrogen storage.")
            return excess_power - kWh_to_store
        return excess_power

    def control_system(self, home, hydrogen_storage_company):
        """Manage the electric company system and interact with the home."""
        grid_deficit, self.market_price = self.monitor_grid()

        if grid_deficit > 0:  # Grid demand exceeds supply, market price may be negative
            excess_power = home.control_system()  # Home handles its power first
            excess_power = self.send_to_hydrogen_storage(excess_power, hydrogen_storage_company)
            print(f"[Grid] Excess power after storage: {excess_power:.2f} kW")
        else:
            print(f"[Grid] No excess power; grid is balanced.")

        return grid_deficit