void setup() {
  Serial.begin(9600); // Start serial communication at 9600 baud
}

void loop() {
  int sensorValue = analogRead(A0); // Read a sensor value (e.g., from pin A0)
  Serial.println(sensorValue); // Send the data over Serial

  if (Serial.available() > 0) {  // Check if data is available
  char command = Serial.read();  // Read the incoming data
  if (command == '1') {  // If the data is '1'
    digitalWrite(LED_PIN, HIGH);  // Turn the LED on
    Serial.println("LED is ON");  // Send confirmation
  } else if (command == '0') {  // If the data is '0'
    digitalWrite(LED_PIN, LOW);  // Turn the LED off
    Serial.println("LED is OFF");  // Send confirmation
  } else {
    Serial.println("Invalid Command");  // Handle invalid input
  }
}
  delay(1000); // Wait for 1 second
}