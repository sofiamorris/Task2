import requests
import json
import zipfile
import io
import apikey
import pandas as pd
import time
from datetime import datetime, timedelta

api_key = apikey.key

# Function to dynamically generate start & end time
def get_time_range():
    """Returns the current and past hour timestamps in the required format."""
    now = datetime.utcnow() - timedelta(days=1)
    one_day_ago = now - timedelta(days=1)
    
    start = one_day_ago.strftime("%Y-%m-%dT%H")
    end = now.strftime("%Y-%m-%dT%H")
    
    return start, end

def get_current_datetime_range():
    """Get the current and next hour in CAISO's datetime format."""
    yesterday = datetime.utcnow() - timedelta(days=2)
    start_time = yesterday.replace(minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    
    # Format as CAISO expects: YYYYMMDDTHH:MM-0000
    start_str = start_time.strftime("%Y%m%dT%H:%M-0000")
    end_str = end_time.strftime("%Y%m%dT%H:%M-0000")
    
    return start_str, end_str

# Function to fetch EIA data (solar generation, net generation, and demand)
def get_eia_data():
    start, end = get_time_range()
    solar_url = (f"https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/"
           f"?frequency=hourly&data[0]=value&facets[fueltype][]=SUN"
           f"&facets[respondent][]=BANC&start=20250211T01&end=20250212T01"
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

    return start, solar_generation, net_generation, demand, solar_penetration


# Function to fetch and process CAISO OASIS LMP data
def get_oasis_data():
    start_time, end_time = get_current_datetime_range()

    nodes = ["CAPTJACK_5_N510", "CAPTJACK_5_N509", "CAPTJACK_5_N511", "CAPTJACK_5_N507", "CAPTJACK_5_N508",
     "STANDFD2_1_N011", "CAPTJACK_5_N506", "CAPTJACK_5_N504", "CAPTJACK_5_N505", "CAPTJACK_5_N512", 
     "CAPTJACK_5_N015", "CAPTJACK_5_N013"]
    nodes_param = ",".join(nodes)

    url = "http://oasis.caiso.com/oasisapi/SingleZip"
    params = {
        "queryname": "PRC_RTPD_LMP",
        "startdatetime": '20250211T01:00-0000',
        "enddatetime": '20250212T01:00-0000',
        "version": "2",
        "resultformat": "6",  # Requesting CSV inside ZIP
        "market_run_id": "RTPD",
        "node": nodes_param,
    }

    response = requests.get(url, params=params)

    if "zip" in response.headers.get("Content-Type", ""):
        with zipfile.ZipFile(io.BytesIO(response.content), "r") as zip_ref:
            file_names = zip_ref.namelist()

            if file_names:
                # Extract CSV file data
                with zip_ref.open(file_names[0]) as file:
                    csv_data = file.read().decode("utf-8")
                    return csv_data
    return None

# Function to process CAISO LMP data
def process_lmp_data(csv_data):
    df = pd.read_csv(io.StringIO(csv_data))

    # Filter for 'LMP' data
    lmp_data = df[df["LMP_TYPE"] == "LMP"]
    
    # Select relevant columns
    lmp_data = lmp_data[["INTERVALSTARTTIME_GMT", "NODE_ID", "PRC"]]
    lmp_data["timestamp"] = pd.to_datetime(lmp_data["INTERVALSTARTTIME_GMT"])

    # Aggregate LMP data per hour
    lmp_data["hour"] = lmp_data["timestamp"].dt.floor("H")

    lmp_data["hour"] = lmp_data["hour"].dt.tz_localize(None)

    hourly_node_lmp = lmp_data.groupby(["hour", "NODE_ID"])["PRC"].mean().reset_index()

    # Aggregate BANC-wide LMP
    banc_avg_lmp = hourly_node_lmp.groupby("hour")["PRC"].mean().reset_index()

    return banc_avg_lmp

def merge_eia_and_caiso_data():
    start, solar_generation, net_generation, demand, solar_penetration = get_eia_data()
    csv_data = get_oasis_data()

    if csv_data:
        banc_avg_lmp = process_lmp_data(csv_data)
        print(f"lmp : {banc_avg_lmp['hour']}")

        # Combine EIA and CAISO data by timestamp
        eia_data = {
            "timestamp": [start],
            "solar_generation": [solar_generation],
            "net_generation": [net_generation],
            "demand": [demand],
            "solar_penetration": [solar_penetration]
        }
        
        eia_df = pd.DataFrame(eia_data)
        print(f"eia: {eia_df['timestamp']}")
        # Convert 'timestamp' to naive datetime to match CAISO data
        eia_df["timestamp"] = pd.to_datetime(eia_df["timestamp"])
        
        # Merge with CAISO LMP data on the 'hour' column
        print(eia_data)
        merged_data = pd.merge(eia_df, banc_avg_lmp, how="left", left_on="timestamp", right_on="hour")

        print(merged_data)
        # Make storage decisions based on solar penetration and LMP
        merged_data = make_storage_decision(merged_data)
        print(merged_data[merged_data["PRC"].notnull()])


        # print(merged_data)

        # Optionally, save merged data to a file
        merged_data.to_csv(f"merged_data_{start}.csv", index=False)
        print(f"Merged data saved to 'merged_data_{start}.csv'")
    else:
        print("No valid LMP data retrieved from CAISO OASIS.")

def make_storage_decision(merged_data):
    """Determine when to store energy based on solar penetration and LMP."""
    storage_decisions = []
    
    for index, row in merged_data.iterrows():
        if row['solar_penetration'] > 100:  # If solar generation exceeds demand
            if row['PRC'] < 0:  # If LMP is low (example threshold)
                storage_decisions.append('Store Hydrogen')
            else:
                storage_decisions.append('Sell Energy')
        else:
            storage_decisions.append('Sell Energy')
    
    merged_data['storage_decision'] = storage_decisions
    return merged_data


# Run the script every hour
if __name__ == "__main__":
    while True:
        merge_eia_and_caiso_data()
        print("Waiting for the next hour...")
        time.sleep(3600)  # Wait for 1 hour before fetching again