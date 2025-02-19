import os
import requests
import time
from datetime import datetime, timedelta


# Base URL for downloading files
BASE_URL = "https://portal.spp.org/file-browser-api/download/lmp-by-settlement-location-weis"

# Directory to save the downloaded files
SAVE_DIR = "spp_data"
os.makedirs(SAVE_DIR, exist_ok=True)

# Directory to save filtered EPE data
EPE_DIR = "epe_data"
os.makedirs(EPE_DIR, exist_ok=True)

# Function to generate file path dynamically
def generate_file_path(year, month, day, hour, minute):
    # Format the file path based on the date and time
    path= f"/{year}/{month}/By_Interval/{day}/WEIS-RTBM-LMP-SL-{year}{month}{day}{hour}{minute}.csv"
    return path

# Function to download a file
def download_file(file_path):
    url = f"{BASE_URL}?path={file_path}"
    response = requests.get(url)
    if response.status_code == 200:
        # Extract the file name and save it
        file_name = file_path.split("/")[-1]
        file_save_path = os.path.join(SAVE_DIR, file_name)
        with open(file_save_path, "wb") as file:
            file.write(response.content)
        print(f"Downloaded: {file_name}")
        return file_save_path
    else:
        print(f"Failed to download file: {file_path}, Status Code: {response.status_code}")
        return None

# Function to filter EPE data
def filter_epe_data(file_path):
    print("file_path")
    try:
        # Read the CSV file
        with open(file_path, "r") as file:
            lines = file.readlines()
        
        # Extract the header and EPE row
        header = lines[0]
        epe_rows = [line for line in lines if "EPE" in line]
        print(epe_rows)
        if epe_rows:
            # Save the filtered data to a new file
            epe_file_name = f"EPE-{os.path.basename(file_path)}"
            epe_file_path = os.path.join(EPE_DIR, epe_file_name)
            with open(epe_file_path, "w") as epe_file:
                epe_file.write(header)  # Write the header
                epe_file.writelines(epe_rows)  # Write the EPE rows
            print(f"EPE data saved to: {epe_file_path}")
        else:
            print("No EPE data found in the file.")
    except Exception as e:
        print(f"Error filtering EPE data: {e}")

# Main function to automate downloads
def automate_downloads():
    while True:
        # Get the current date and time
        now = datetime.now()
        year = now.year
        month = f"{now.month:02d}"
        day = f"{now.day:02d}"
        hour = now.hour
        minute = now.minute // 5 * 5

        # Generate the file path
        file_path = generate_file_path(year, month, day, hour, minute)

        try:
            # Download the file
            downloaded_file = download_file(file_path)
            if downloaded_file:
                # Filter EPE data
                filter_epe_data(downloaded_file)

        except Exception as e:
            print(f"Error during download: {e}")

        # Wait for 5 minutes before the next iteration
        time.sleep(300)  # 300 seconds = 5 minutes

# Start the automation
if __name__ == "__main__":
    automate_downloads()
