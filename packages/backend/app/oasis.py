import requests
import zipfile
import io
import pandas as pd
from datetime import datetime, timedelta

def get_current_datetime_range():
    """Get the current and next hour in CAISO's datetime format."""
    now = datetime.utcnow()
    start_time = now.replace(minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    
    # Format as CAISO expects: YYYYMMDDTHH:MM-0000
    start_str = start_time.strftime("%Y%m%dT%H:%M-0000")
    end_str = end_time.strftime("%Y%m%dT%H:%M-0000")
    
    return start_str, end_str

def get_oasis_data():
    """Fetches and extracts real-time LMP data from CAISO OASIS API (ZIP format)."""

    start_time, end_time = get_current_datetime_range()

    url = "http://oasis.caiso.com/oasisapi/SingleZip"
    params = {
        "queryname": "PRC_RTPD_LMP",
        "startdatetime": start_time,
        "enddatetime": end_time,
        "version": "2",
        "resultformat": "6",  # Requesting CSV inside ZIP
        "market_run_id": "RTPD",
        "node": "4C687_1_B1"
    }

    response = requests.get(url, params=params)

    # Print the content type for debugging
    content_type = response.headers.get("Content-Type", "")
    print("Content-Type:", content_type)
    print("Request URL:", response.url)

    # If the response is a ZIP file
    if "zip" in content_type:
        with zipfile.ZipFile(io.BytesIO(response.content), "r") as zip_ref:
            file_names = zip_ref.namelist()
            print("Files in ZIP:", file_names)

            if not file_names:
                print("No files found in ZIP archive.")
                return None

            # Extract and read the first CSV file
            with zip_ref.open(file_names[0]) as file:
                csv_data = file.read().decode("utf-8")
                return csv_data

    print("Unexpected response format.")
    return None

def save_csv_to_file(csv_data, filename):
    """Save the CSV data to a file."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(csv_data)
    print(f"Data saved to {filename}")

def parse_csv_to_dataframe(csv_data):
    """Convert raw CSV text into a Pandas DataFrame."""
    try:
        df = pd.read_csv(io.StringIO(csv_data))
        return df
    except pd.errors.ParserError as e:
        print("CSV Parsing Error:", e)
        return None

# 🔥 Run the script
csv_data = get_oasis_data()

if csv_data:
    # Save data to file
    filename = f"CAISO_LMP_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.csv"
    save_csv_to_file(csv_data, filename)

    # Parse and display data
    df = parse_csv_to_dataframe(csv_data)
    if df is not None:
        print(df.head())  # Show first few rows
    else:
        print("Failed to parse CSV data.")
else:
    print("No data retrieved from CAISO OASIS.")
