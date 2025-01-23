import serial
import time
from scipy.io import savemat

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

        """Send a command to the Arduino."""
        ser.write(command.encode())  # Send the command
        response = ser.readline().decode('utf-8').strip()  # Read the response
        print(f"Arduino response: {response}")

        try:
            while True:
                user_input = input("Enter '1' to turn ON the LED or '0' to turn it OFF: ")
                if user_input in ['1', '0']:
                    send_command(user_input)  # Send the command
                else:
                    print("Invalid input. Please enter '1' or '0'.")

except serial.SerialException as e:
    print(f"Error: {e}")
except KeyboardInterrupt:
    print("Exiting program.")

