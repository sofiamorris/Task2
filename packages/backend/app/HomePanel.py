import random

class HomePanel:
    def __init__(self):
        self.solar_generation = 0  # kW
        self.local_consumption = 0  # kW
        self.hydrogen_storage = {"stored_energy": 50, "max_capacity": 100, "conversion_rate": 2}  # kWh
        self.export_limit = 5  # kW

    def generate_power(self):
        """Simulate solar power generation."""
        self.solar_generation = round(random.uniform(5, 15), 2)
        print(f"[Home] Solar generation: {self.solar_generation} kW")

    def consume_power(self):
        """Simulate local power consumption."""
        self.local_consumption = round(random.uniform(3, 12), 2)
        print(f"[Home] Local consumption: {self.local_consumption} kW")

    def export_to_grid(self, net_power):
        """Export electricity to the grid."""
        exportable = max(0, min(net_power, self.export_limit))
        print(f"[Home] Exported {exportable:.2f} kW to the grid.")
        # change so that electric company will know that the grid receives "5 kw"
        return net_power - exportable

    def control_system(self):
        """Manage the home system."""
        self.generate_power()
        self.consume_power()

        # Calculate net power
        net_power = self.solar_generation - self.local_consumption
        print(f"[Home] Net power: {net_power:.2f} kW")

        if net_power > 0:
            storage_power = self.export_to_grid(net_power)
            # return value sent to grid
        else:
            # receive from grid function
            # return value needed from grid
        return storage_power