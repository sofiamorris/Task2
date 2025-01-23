import HomePanel
import ElectricCompany
import random

class HydrogenStorage:
    def __init__(self):
        self.stored_energy = 0  # kWh
        self.storage_fee = 20  # $/MWh to store energy
        self.selling_price = 50  # $/MWh when energy is sold back

    def available_capacity(self):
        """Return the remaining capacity for energy storage."""
        return 100000 - self.stored_energy  # 100,000 kWh max capacity

    def store_energy(self, energy_kWh):
        """Store energy in the hydrogen system."""
        if self.available_capacity() >= energy_kWh:
            self.stored_energy += energy_kWh
            print(f"[Hydrogen Storage] Stored {energy_kWh} kWh. Total stored: {self.stored_energy} kWh.")
        else:
            print("[Hydrogen Storage] Not enough capacity to store energy.")

    def profit_from_storage(self):
        """Calculate the profit from storing and selling energy."""
        profit = (self.stored_energy / 1000) * self.selling_price  # Convert kWh to MWh for selling
        print(f"[Hydrogen Storage] Profit from storage: ${profit:.2f}")
        return profit


# Simulation
if __name__ == "__main__":
    home = HomePanel.HomePanel()
    electric_company = ElectricCompany.ElectricCompany()
    hydrogen_storage_company = HydrogenStorage()

    for step in range(5):
        print(f"\n--- Simulation Step {step + 1} ---")
        grid_deficit = electric_company.control_system(home, hydrogen_storage_company)

        if grid_deficit <= 0:
            hydrogen_storage_company.profit_from_storage()