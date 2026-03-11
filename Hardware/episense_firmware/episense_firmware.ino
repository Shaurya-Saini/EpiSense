/*
 * EpiSense — ESP32 Environmental Sensor Firmware
 *
 * Reads TDS, turbidity, and water temperature sensors,
 * then transmits the data as JSON to the backend server
 * via HTTP POST over WiFi.
 *
 * Hardware Connections:
 *   - TDS Sensor        → GPIO 34 (Analog)
 *   - Turbidity Sensor  → GPIO 35 (Analog)
 *   - DS18B20 Temp      → GPIO 4  (Digital, OneWire)
 *
 * Libraries Required:
 *   - WiFi.h          (built-in ESP32)
 *   - HTTPClient.h    (built-in ESP32)
 *   - ArduinoJson.h   (install via Library Manager)
 *   - OneWire.h       (install via Library Manager)
 *   - DallasTemperature.h (install via Library Manager)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// ── Configuration ───────────────────────────────────────────────────
// WiFi credentials — update these for your network
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// Backend server URL — update with your server's IP address
const char* SERVER_URL = "http://192.168.1.100:8000/api/sensor-data";

// Sensor reading interval (milliseconds)
const unsigned long READ_INTERVAL = 10000;  // 10 seconds

// ── Pin Definitions ─────────────────────────────────────────────────
#define TDS_PIN         34    // Analog input for TDS sensor
#define TURBIDITY_PIN   35    // Analog input for turbidity sensor
#define TEMP_PIN        4     // Digital pin for DS18B20 temperature sensor

// ── Sensor Calibration Constants ────────────────────────────────────
#define VREF            3.3   // ESP32 ADC reference voltage
#define ADC_RESOLUTION  4095  // 12-bit ADC

// ── OneWire & Temperature Sensor Setup ──────────────────────────────
OneWire oneWire(TEMP_PIN);
DallasTemperature tempSensor(&oneWire);

// ── Timing ──────────────────────────────────────────────────────────
unsigned long lastReadTime = 0;


void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("========================================");
    Serial.println("  EpiSense — Environmental Sensor Node");
    Serial.println("========================================");

    // Initialize sensor pins
    pinMode(TDS_PIN, INPUT);
    pinMode(TURBIDITY_PIN, INPUT);

    // Initialize temperature sensor
    tempSensor.begin();

    // Connect to WiFi
    connectWiFi();
}


void loop() {
    unsigned long currentTime = millis();

    // Read and transmit sensor data at the configured interval
    if (currentTime - lastReadTime >= READ_INTERVAL) {
        lastReadTime = currentTime;

        // Ensure WiFi is still connected
        if (WiFi.status() != WL_CONNECTED) {
            Serial.println("[WARN] WiFi disconnected. Reconnecting...");
            connectWiFi();
        }

        // Read all sensors
        float tdsValue       = readTDS();
        float turbidityValue = readTurbidity();
        float temperatureValue = readTemperature();

        // Print readings to Serial Monitor
        Serial.println("--- Sensor Readings ---");
        Serial.printf("  TDS:         %.2f ppm\n", tdsValue);
        Serial.printf("  Turbidity:   %.2f NTU\n", turbidityValue);
        Serial.printf("  Temperature: %.2f °C\n", temperatureValue);

        // Send data to backend
        sendData(tdsValue, turbidityValue, temperatureValue);
    }
}


// ── WiFi Connection ─────────────────────────────────────────────────
void connectWiFi() {
    Serial.printf("[INFO] Connecting to WiFi: %s", WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println();
        Serial.printf("[INFO] Connected! IP: %s\n", WiFi.localIP().toString().c_str());
    } else {
        Serial.println();
        Serial.println("[ERROR] WiFi connection failed. Will retry next cycle.");
    }
}


// ── TDS Sensor Reading ──────────────────────────────────────────────
float readTDS() {
    // Average multiple readings for stability
    int readings = 0;
    for (int i = 0; i < 10; i++) {
        readings += analogRead(TDS_PIN);
        delay(10);
    }
    float avgReading = readings / 10.0;

    // Convert analog reading to voltage
    float voltage = avgReading * VREF / ADC_RESOLUTION;

    // Convert voltage to TDS value (ppm)
    // Formula based on typical TDS sensor calibration
    float tds = (133.42 * voltage * voltage * voltage
               - 255.86 * voltage * voltage
               + 857.39 * voltage) * 0.5;

    return max(0.0f, tds);  // Ensure non-negative
}


// ── Turbidity Sensor Reading ────────────────────────────────────────
float readTurbidity() {
    // Average multiple readings for stability
    int readings = 0;
    for (int i = 0; i < 10; i++) {
        readings += analogRead(TURBIDITY_PIN);
        delay(10);
    }
    float avgReading = readings / 10.0;

    // Convert analog reading to voltage
    float voltage = avgReading * VREF / ADC_RESOLUTION;

    // Convert voltage to NTU (Nephelometric Turbidity Units)
    // Higher voltage = clearer water = lower NTU
    float ntu = -1120.4 * voltage * voltage + 5742.3 * voltage - 4353.8;

    return max(0.0f, ntu);  // Ensure non-negative
}


// ── Temperature Sensor Reading ──────────────────────────────────────
float readTemperature() {
    tempSensor.requestTemperatures();
    float tempC = tempSensor.getTempCByIndex(0);

    // Check for sensor error
    if (tempC == DEVICE_DISCONNECTED_C) {
        Serial.println("[WARN] Temperature sensor not connected!");
        return 25.0;  // Return default value
    }

    return tempC;
}


// ── HTTP POST Data Transmission ─────────────────────────────────────
void sendData(float tds, float turbidity, float temperature) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("[ERROR] Cannot send data — WiFi not connected.");
        return;
    }

    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");

    // Build JSON payload
    JsonDocument doc;
    doc["tds"] = round(tds * 100) / 100.0;
    doc["turbidity"] = round(turbidity * 100) / 100.0;
    doc["temperature"] = round(temperature * 100) / 100.0;

    String payload;
    serializeJson(doc, payload);

    Serial.printf("[INFO] Sending: %s\n", payload.c_str());

    // Send POST request
    int httpCode = http.POST(payload);

    if (httpCode > 0) {
        Serial.printf("[INFO] Server response: %d\n", httpCode);
        if (httpCode == 200) {
            String response = http.getString();
            Serial.printf("[INFO] Response: %s\n", response.c_str());
        }
    } else {
        Serial.printf("[ERROR] POST failed: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end();
}
