ESP32 WATER QUALITY PROJECT (TDS + TURBIDITY)

---

## CONNECTIONS

1. TDS SENSOR

TDS Module Pins:

+ → ESP32 3.3V
- → ESP32 GND
A → ESP32 GPIO35

Notes:

* No resistor required
* Safe direct connection

2. TURBIDITY SENSOR

Pins:
VCC → ESP32 5V (VIN)
GND → ESP32 GND
OUT → Voltage Divider → GPIO34

Voltage Divider (using two 1kΩ resistors):

OUT ─── 1kΩ ─── GPIO34
│
1kΩ
│
GND

Notes:

* Divider is mandatory to protect ESP32
* Do NOT connect OUT directly to ESP32

---

## CODE (COMBINED)

#define TDS_PIN 35
#define TURBIDITY_PIN 34

void setup() {
Serial.begin(115200);

analogReadResolution(12);
analogSetAttenuation(ADC_11db);
}

float getTDS() {
int samples = 30;
float sum = 0;

for (int i = 0; i < samples; i++) {
sum += analogRead(TDS_PIN);
delay(5);
}

float avg = sum / samples;
float voltage = avg * (3.3 / 4095.0);

float compensatedVoltage = voltage;

float tds = (133.42 * compensatedVoltage * compensatedVoltage * compensatedVoltage
- 255.86 * compensatedVoltage * compensatedVoltage
+ 857.39 * compensatedVoltage) * 0.5;

return tds;
}

float getTurbidity() {
int samples = 30;
float sum = 0;

for (int i = 0; i < samples; i++) {
sum += analogRead(TURBIDITY_PIN);
delay(5);
}

float avg = sum / samples;
float voltage = avg * (3.3 / 4095.0);

float actualVoltage = voltage * 2.0; // compensate divider

float turbidity = map(actualVoltage * 100, 0, 300, 100, 0);

return turbidity;
}

void loop() {
float tdsValue = getTDS();
float turbidityValue = getTurbidity();

Serial.println("-----------------------------");

Serial.print("TDS: ");
Serial.print(tdsValue, 0);
Serial.println(" ppm");

Serial.print("Turbidity: ");
Serial.print(turbidityValue, 0);
Serial.println(" /100");

Serial.println("-----------------------------\n");

delay(2000);
}

---

## FINAL NOTES

* TDS gives approximate ppm values
* Turbidity is relative (0–100 scale)
* Both sensors are now safely connected to ESP32
* Can be extended later with temperature + ML
