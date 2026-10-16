// Light sender for the ESP32: blinks a message out on the LED (GPIO 4).
// Protocol must match light_receiver.py on the Pi.

const int LED_PIN = 4;
const int BIT_MS  = 100;   // 10 bits/sec -- photoresistors are slow, don't go much faster

const char message[] = "Hello from the ESP32 over light!";

void sendByte(uint8_t b) {
  digitalWrite(LED_PIN, HIGH);              // start bit (light ON)
  delay(BIT_MS);
  for (int i = 0; i < 8; i++) {             // 8 data bits, LSB first
    digitalWrite(LED_PIN, (b >> i) & 1);
    delay(BIT_MS);
  }
  digitalWrite(LED_PIN, LOW);               // stop bit + small gap (light OFF)
  delay(BIT_MS * 2);
}

void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  delay(3000);
}

void loop() {
  size_t len = strlen(message);
  uint8_t sum = 0;

  //Serial.println("Sending Message");
  sendByte(0xAA);                           // sync header
  sendByte(0x55);

  sendByte(len >> 8);                       // length
  sendByte(len & 0xFF);

  for (size_t i = 0; i < len; i++) {        // data
    sendByte(message[i]);
    sum += message[i];
  }
  
  sendByte(sum);                            // checksum

  //Serial.println("Message sent");
  delay(10000);                             // wait, then send again
}
