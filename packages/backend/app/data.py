import serial
from scipy.io import savemat
from google.cloud import bigquery
import random
import time
from datetime import datetime

# Initialize BigQuery Client
client = bigquery.Client()

# BigQuery Table Details
project_id = "your-project-id"
dataset_id = "sensor_data"
table_id = "readings"
table_ref = f"{project_id}.{dataset_id}.{table_id}"

# Function to insert data into BigQuery
def insert_into_bigquery(data):
    rows_to_insert = [data]
    errors = client.insert_rows_json(table_ref, rows_to_insert)
    if errors:
        print("Error inserting data:", errors)
    else:
        print("Data inserted successfully:", data)

def get_sensor_data():
    # Define the serial port and baud rate
    arduino_port = "/dev/ttyUSB0"  # Replace with the correct port (e.g., COM3 on Windows, /dev/ttyUSB0 on Linux)
    baud_rate = 9600

    try:
        # Initialize the serial connection
        with serial.Serial(arduino_port, baud_rate, timeout=1) as ser:
            print(f"Connected to Arduino on {arduino_port} at {baud_rate} baud.")
            
            # Give the Arduino time to reset
            time.sleep(2)
            
            # Read data continuously
            while True:
                line = ser.readline()  # Read a line of data
                if line:
                    # Decode bytes to string and strip any whitespace
                    data = line.decode('utf-8').strip()
                    print(f"Received: {data}")
                    
            data = {
                "Timestamp": [time.time() for _ in range(10)],  # Replace with actual timestamps
                "SensorValue": [i * 10 for i in range(10)]      # Replace with actual sensor values
            }
            savemat("sensor_data.mat", data)

            return data



    except serial.SerialException as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Exiting program.")

# Continuous Data Collection
while True:
    sensor_data = get_sensor_data()
    insert_into_bigquery(sensor_data)
    time.sleep(5)  # Adjust the interval as needed
