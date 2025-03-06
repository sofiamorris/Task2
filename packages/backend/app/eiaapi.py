import requests
import apikey
import json
import time
from datetime import datetime, timedelta

api_key = apikey.key

# Function to dynamically generate start & end time
def get_time_range():
    """Returns the current and past hour timestamps in the required format."""
    now = datetime.utcnow() - timedelta(days=1)
    one_hour_ago = now - timedelta(days=1)
    
    start = one_hour_ago.strftime("%Y-%m-%dT%H")
    end = now.strftime("%Y-%m-%dT%H")
    
    return start, end

# Function to get data from EIA API
def get_eia_data():
    start, end = get_time_range()
    solar_url = (f"https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/"
           f"?frequency=hourly&data[0]=value&facets[fueltype][]=SUN"
           f"&facets[respondent][]=BANC&start={start}&end={end}"
           f"&sort[0][column]=period&sort[0][direction]=desc&offset=0"
           f"&length=5000&api_key={api_key}")

    response = requests.get(solar_url)
    
    if response.status_code == 200:
        data = response.json()
        solar_data = data.get('response', {}).get('data', [])
        solar_generation = sum(float(entry['value']) for entry in solar_data if entry.get('value') and entry['value'].replace('.', '', 1).isdigit())

        # Save to file
        with open("eia_data.json", "a") as file:
            json.dump(data, file, indent=4)
            file.write("\n")
    else:
        solar_generation = None

    region_url = (f"https://api.eia.gov/v2/electricity/rto/region-data/data/"
           f"?frequency=hourly&data[0]=value&facets[respondent][]=BANC"
           f"&start={start}&end={end}"
           f"&sort[0][column]=period&sort[0][direction]=desc"
           f"&offset=0&length=5000&api_key={api_key}")

    response = requests.get(region_url)
    
    if response.status_code == 200:
        data = response.json()
        region_data = data.get('response', {}).get('data', [])

        demand = next((entry['value'] for entry in region_data if entry.get('type') == "D"), None)
        net_generation = next((entry['value'] for entry in region_data if entry.get('type') == "NG"), None)

        # Save to file
        with open("eia_data.json", "a") as file:
            json.dump(data, file, indent=4)
            file.write("\n")
    else:
        demand, net_generation = None, None

    if demand:
        demand = float(demand)

    # Compute Solar Penetration
    if solar_generation is not None and demand:
        solar_penetration = (solar_generation / demand) * 100
    else:
        solar_penetration = None

    # Save to file
    data_entry = {
        "timestamp": start,
        "solar_generation": solar_generation,
        "net_generation": net_generation,
        "demand": demand,
        "solar_penetration": solar_penetration
    }

    with open("eia_solar_data.json", "a") as file:
        json.dump(data_entry, file, indent=4)
        file.write("\n")

    # Print Data Summary
    print(f"\nData for {start}:")
    print(f"\tSolar Generation: {solar_generation} MW")
    print(f"\tTotal Net Generation: {net_generation} MW")
    print(f"\tDemand: {demand} MW")
    print(f"\tSolar Penetration: {solar_penetration:.2f}%")

# Run the function every hour indefinitely
if __name__ == "__main__":
    while True:
        get_eia_data()
        print("Waiting for the next hour...")
        time.sleep(3600)  # Wait 1 hour before fetching again