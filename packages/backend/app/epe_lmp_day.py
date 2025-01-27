import requests
import pandas as pd
from bs4 import BeautifulSoup
import io

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
    
    return epe_data

# Step 4: Main Function
def main():
    file_links = fetch_file_links()
    
    # Iterate through each file link and process it
    for link in file_links:
        print(f"Processing file: {link}")
        try:
            epe_data = process_file(link)
            print(epe_data[['Interval', 'LMP']])  # Display relevant data
        except Exception as e:
            print(f"Error processing file {link}: {e}")

if __name__ == "__main__":
    main()
