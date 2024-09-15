void setup() {
  pinMode(4, OUTPUT); // Initialize pin 4 as an output
  pinMode(7, OUTPUT); // Initialize pin 6 as an output for the second light
  Serial.begin(9600); // Start serial communication at 9600 baud
  

}

// The blink function
void blink(int pin, int delayTime) {
  digitalWrite(pin, HIGH);  // Turn the LED on
  delay(delayTime);         // Wait for the specified delay time
  digitalWrite(pin, LOW);   // Turn the LED off
  delay(delayTime);         // Wait for the specified delay time
}

void loop() {
  if (Serial.available() > 0) { // Check if data is available to read
    char command = Serial.read(); // Read the incoming byte
    if (command == 'c') 
    { // If the command is 'c', blink the LED on pin 6
     // Blink the LED on pin 6 with a 1-second delay
      blink(7, 1000);
    }
    if (command == 'b') 
    { // If the command is 'b', blink the LED on pin 4
      blink(4, 1000); // Blink the LED on pin 4 with a 1-second delay
    } 
  }
}

void blink2(int pin, int delayTime) 
{
    digitalWrite(pin, HIGH);  // Turn the LED on
  delay(delayTime);         // Wait for the specified delay time
  digitalWrite(pin, LOW);   // Turn the LED off
  delay(delayTime);         // Wait for the specified delay time

}