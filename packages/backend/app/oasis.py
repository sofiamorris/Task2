import requests
import zipfile
import io
import pandas as pd
import time
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

    nodes = ["CAPTJACK_5_N510", "CAPTJACK_5_N509", "CAPTJACK_5_N511", "CAPTJACK_5_N507", "CAPTJACK_5_N508",
     "STANDFD2_1_N011", "CAPTJACK_5_N506", "CAPTJACK_5_N504", "CAPTJACK_5_N505", "CAPTJACK_5_N512", 
     "CAPTJACK_5_N015", "CAPTJACK_5_N013"]
    nodes_param = ",".join(nodes)

    url = "http://oasis.caiso.com/oasisapi/SingleZip"
    params = {
        "queryname": "PRC_RTPD_LMP",
        "startdatetime": start_time,
        "enddatetime": end_time,
        "version": "2",
        "resultformat": "6",  # Requesting CSV inside ZIP
        "market_run_id": "RTPD",
        "node": nodes_param,
    }

    response = requests.get(url, params=params)

    # Print the content type for debugging
    content_type = response.headers.get("Content-Type", "")
    print("\nFetching Data...")
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
    print(f"✅ Data saved to {filename}")

def parse_csv_to_dataframe(csv_data):
    """Convert raw CSV text into a Pandas DataFrame."""
    try:
        df = pd.read_csv(io.StringIO(csv_data))
        return df
    except pd.errors.ParserError as e:
        print("CSV Parsing Error:", e)
        return None

# 🔥 Run the script every hour
if __name__ == "__main__":
    while True:
        csv_data = get_oasis_data()

        if csv_data:
            # Save data to a timestamped file
            filename = f"CAISO_LMP_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.csv"
            save_csv_to_file(csv_data, filename)

        # Parse and display data
        df = parse_csv_to_dataframe(csv_data)

        if df is not None:
            # Assuming 'df' is the parsed DataFrame from CAISO OASIS
            # Filter to keep only rows where LMP_TYPE is 'LMP' (total LMP)
            lmp_data = df[df["LMP_TYPE"] == "LMP"]

            # Select relevant columns
            lmp_data = lmp_data[["INTERVALSTARTTIME_GMT", "NODE_ID", "PRC"]]

            # Rename 'PRC' column to 'LMP' for clarity
            lmp_data.rename(columns={"PRC": "LMP"}, inplace=True)

            # Convert INTERVALSTARTTIME_GMT to datetime for easier manipulation
            lmp_data["timestamp"] = pd.to_datetime(lmp_data["INTERVALSTARTTIME_GMT"])

            # Extract the hour from the timestamp for grouping
            lmp_data["hour"] = lmp_data["timestamp"].dt.floor("H")  # Rounds down to the start of the hour

            # Ensure the NODE column is included
            if "NODE_ID" in lmp_data.columns:
                # Convert timestamps to hourly format
                lmp_data["hour"] = lmp_data["timestamp"].dt.floor("H")  # Rounds down to the start of the hour

                # First, average LMP across 15-min intervals for each NODE per hour
                hourly_node_lmp = lmp_data.groupby(["hour", "NODE_ID"])["LMP"].mean().reset_index()

                # Then, take the average of all nodes for each hour to get BANC-wide LMP
                banc_avg_lmp = hourly_node_lmp.groupby("hour")["LMP"].mean().reset_index()

                # Save the BANC-wide hourly LMP data
                filename = f"LMP_BANC_HOURLY_AVG_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.csv"
                hourly_node_lmp.to_csv(filename, index=False)
                print(f"✅ BANC-wide hourly average LMP saved to {filename}")

                # Show results
                print(banc_avg_lmp.head())

            # # Optionally, save to a file
            # filename = f"LMP_AVG_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.csv"
            # lmp_data.to_csv(filename, index=False)
            # print(f"LMP data saved to {filename}")
        else:
            print("No valid LMP data retrieved from CAISO OASIS.")


        print("Waiting for the next hour...\n")
        time.sleep(3600)  # Wait for 1 hour
