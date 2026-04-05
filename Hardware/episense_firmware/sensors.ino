
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