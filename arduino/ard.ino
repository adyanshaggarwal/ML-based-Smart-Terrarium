#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

int lightPin = A1;
int soilPin = A2; 
const int pumpPin = 8;
const int fanPin = 10;
int inter = 20000;
int interval=inter;
int pumpt=3000;
int fant=10000;
void setup() {
  Serial.begin(9600);
  dht.begin();
  pinMode(pumpPin, OUTPUT);
  pinMode(fanPin, OUTPUT);
  digitalWrite(pumpPin, LOW);
  digitalWrite(fanPin, LOW);


  delay(2000);
}

void loop() {
  float temp = dht.readTemperature();
  float humidity = dht.readHumidity();

  int lightRaw = analogRead(lightPin);
  float light = map(lightRaw, 0, 1023, 0, 1000);  // adjust as needed
  int soilRaw = analogRead(soilPin);
  float soil = map(soilRaw, 1023, 0, 0, 100); 


  // Send sensor data as CSV to Python
  Serial.print(soil); Serial.print(",");
  Serial.print(temp); Serial.print(",");
  Serial.print(humidity); Serial.print(",");
  Serial.println(light);

  delay(3000);  // Wait for response from Python

  // Read correction values from Python
  if (Serial.available()) {
    String correction = Serial.readStringUntil('\n');
    float soilCorr = 0, humidCorr = 0;

    int commaIndex = correction.indexOf(',');
    if (commaIndex > 0) {
      soilCorr = correction.substring(0, commaIndex).toFloat();
      humidCorr = correction.substring(commaIndex + 1).toFloat();

      Serial.print("🔧 Corrections → Soil: ");
      Serial.print(soilCorr);
      Serial.print(" | Humidity: ");
      Serial.println(humidCorr);

      if (soilCorr > 5) {
        Serial.println("💧 Water pump ON (3s)");
        digitalWrite(pumpPin, HIGH);
        delay(pumpt);
        interval=interval-pumpt;
        digitalWrite(pumpPin, LOW);
      }

      if (humidCorr > 5) {
        Serial.println("🌬️ Fan ON (10s)");
        digitalWrite(fanPin, HIGH);
        delay(fant);
        interval= interval-fant;
        digitalWrite(fanPin, LOW);
      }
    }
  }

  delay(interval);
  interval=inter;//
}
