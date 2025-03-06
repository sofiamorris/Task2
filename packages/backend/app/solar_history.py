import os
import requests
import pandas as pd
import io
from datetime import datetime, timedelta
import apikey

api_key = apikey.key
BASE_URL = "https://portal.spp.org/file-browser-api/download/lmp-by-settlement-location-weis"

# Function to generate file paths
def generate_file_paths(days_ago, intervals=12):
    now = datetime.utcnow() - timedelta(days=days_ago+1)
    year = now.year
    month = f"{now.month:02d}"
    day = f"{now.day:02d}"
    
    file_paths = [
        f"/{year}/{month}/By_Interval/{day}/WEIS-RTBM-LMP-SL-{year}{month}{day}{hour:02d}00.csv"
        for hour in range(1, 24, 24 // intervals)
    ]
    return file_paths

# Function to fetch and process LMP data
def fetch_lmp_data(file_path):
    url = f"{BASE_URL}?path={file_path}"
    response = requests.get(url, timeout=30)  # 30-second timeout
    
    if response.status_code == 200:
        try:
            df = pd.read_csv(io.StringIO(response.text))
            epe_rows = df[df['Settlement Location'].str.contains("IID", na=False)]
            if not epe_rows.empty:
                return epe_rows["Interval"].iloc[0], epe_rows["LMP"].mean()
        except Exception as e:
            print(f"Error processing LMP data: {e}")
    else:
        print(f"Failed to download file: {file_path}")
    
    return None, None

# Function to fetch EIA data
def get_eia_data(start, end):
    solar_url = (f"https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/"
                 f"?frequency=hourly&data[0]=value&facets[fueltype][]=SUN"
                 f"&facets[respondent][]=IID&start={start}&end={end}"
                 f"&sort[0][column]=period&sort[0][direction]=desc&api_key={api_key}")
    
    response = requests.get(solar_url, timeout=30)  # 30-second timeout
    solar_generation = None
    if response.status_code == 200:
        data = response.json().get('response', {}).get('data', [])
        solar_generation = sum(float(entry['value']) for entry in data if entry.get('value'))
    
    region_url = (f"https://api.eia.gov/v2/electricity/rto/region-data/data/"
                  f"?frequency=hourly&data[0]=value&facets[respondent][]=IID"
                  f"&start={start}&end={end}"
                  f"&sort[0][column]=period&sort[0][direction]=desc&api_key={api_key}")
    
    response = requests.get(region_url)
    demand, net_generation = None, None
    if response.status_code == 200:
        data = response.json().get('response', {}).get('data', [])
        demand = next((entry['value'] for entry in data if entry.get('type') == "D"), None)
        net_generation = next((entry['value'] for entry in data if entry.get('type') == "NG"), None)
    
    return solar_generation, net_generation, demand

# Function to merge and save data
def merge_eia_and_epe(days_ago):
    merged_data = []
    
    for day in range(1, days_ago + 1):  # Start from 1 to ensure we only fetch past data
        start_time = (datetime.utcnow() - timedelta(days=day)).strftime("%Y-%m-%dT%H")
        end_time = (datetime.utcnow() - timedelta(days=day-1)).strftime("%Y-%m-%dT%H")
        
        solar_generation, net_generation, demand = get_eia_data(start_time, end_time)
        
        for file_path in generate_file_paths(day):
            timestamp, lmp_value = fetch_lmp_data(file_path)
            if timestamp and lmp_value:
                merged_data.append({
                    "timestamp": timestamp,
                    "solar_generation": solar_generation,
                    "net_generation": net_generation,
                    "demand": demand,
                    "LMP": lmp_value
                })
    
    if merged_data:
        pd.DataFrame(merged_data).to_csv("iid_merged_data.csv", index=False)
        print("Merged data saved to merged_data.csv")
    else:
        print("No data available for merging.")

if __name__ == "__main__":
    merge_eia_and_epe(365)
