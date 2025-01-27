import requests
import pandas as pd
from bs4 import BeautifulSoup
import io
import time

# Step 1: Base URL for the SPP Market Data
BASE_URL = "https://portal.spp.org/pages/lmp-by-settlement-location-weis"

# Step 2: Fetch the webpage containing the file links
def fetch_file_links():
    response = requests.get(BASE_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract file links (adjust based on website structure)
    links = [
        a['href'] for a in soup.find_all('a', href=True)
        if "csv" in a['href']  # Filter for CSV files
    ]
    return links

# Step 3: Download and Process Each File
def process_file(file_url):
    response = requests.get(file_url)
    response.raise_for_status()
    
    # Load CSV content into pandas DataFrame
    data = pd.read_csv(io.StringIO(response.text))
    
    # Filter for EPE settlement location
    epe_data = data[data['Settlement Location'] == 'EPE']
    
    # Return filtered data
    return epe_data[['Interval', 'LMP']]

# Step 4: Main Function to Query and Process
def query_data():
    try:
        file_links = fetch_file_links()
        
        # Process the latest file (if sorted by date or priority)
        if file_links:
            latest_file = file_links[0]  # Adjust logic if files need ordering
            print(f"Processing file: {latest_file}")
            epe_data = process_file(latest_file)
            print(epe_data)  # Display the results
        else:
            print("No files available.")
    except Exception as e:
        print(f"Error: {e}")

# Step 5: Schedule the Task Every 5 Minutes
def run_every_5_minutes():
    while True:
        print(f"Running query at {pd.Timestamp.now()}")
        query_data()
        print("Waiting for 5 minutes...")
        time.sleep(300)  # Wait 5 minutes (300 seconds)

if __name__ == "__main__":
    run_every_5_minutes()
