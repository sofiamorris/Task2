import requests
import pandas as pd

# Define the OASIS API URL and parameters
url = "http://oasis.caiso.com/oasisapi/SingleZip"
params = {
    "queryname": "PRC_LMP",
    "market_run_id": "RT5M",  # Real-time 5-minute market
    "startdatetime": "20250107T07:00-0000",  # Format: YYYYMMDDTHH:MM-0000
    "enddatetime": "20250107T08:00-0000",
    "version": "1",
    "resultformat": "6"  # CSV output
}

# Send the request
response = requests.get(url, params=params)

# Save the response
with open("prices.zip", "wb") as file:
    file.write(response.content)

# Extract and read the CSV file
import zipfile
with zipfile.ZipFile("prices.zip", 'r') as zip_ref:
    zip_ref.extractall("output")

# Load the CSV file to analyze
df = pd.read_csv("output/your_csv_file.csv")  # Replace with the extracted file name
print(df.head())
