#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ── Pin Definitions ──────────────────────────────────────────────────
#define TDS_PIN        35
#define TURBIDITY_PIN  34

// ── WiFi & Backend Configuration ────────────────────────────────────
const char* WIFI_SSID     = "Poison ";
const char* WIFI_PASSWORD = "Shaurya3003";
const char* SERVER_URL    = "http://192.168.19.151:8000/api/sensor-data";

// How often to read sensors and POST (milliseconds)
const unsigned long SEND_INTERVAL = 10000;  // 10 seconds

// ── Hardcoded Temperature (sensor non-functional) ────────────────────
const float TEMP_BASE = 24.0;   // °C — baseline hardcoded value

// ── Timing ──────────────────────────────────────────────────────────
unsigned long lastSendTime = 0;
unsigned int  sendCount    = 0;


// ════════════════════════════════════════════════════════════════════
void setup() {
    Serial.begin(115200);
    delay(1000);

    analogReadResolution(12);
    analogSetAttenuation(ADC_11db);

    Serial.println();
    Serial.println("============================================");
    Serial.println("        EpiSense — Water Quality IoT");
    Serial.println("============================================");
    Serial.println("  [!] Temperature is HARDCODED (sensor N/A)");
    Serial.println("============================================");
    Serial.println();

    connectWiFi();

    Serial.println("[INFO] Running initial read + POST...");
    runCycle();
    lastSendTime = millis();
}


// ════════════════════════════════════════════════════════════════════
void loop() {
    unsigned long now = millis();

    if (now - lastSendTime >= SEND_INTERVAL) {
        lastSendTime = now;

        if (WiFi.status() != WL_CONNECTED) {
            Serial.println("[WARN] WiFi dropped. Reconnecting...");
            connectWiFi();
        }

        runCycle();
    }
}


// ── Main Sensor + POST Cycle ─────────────────────────────────────────
void runCycle() {
    sendCount++;
    Serial.printf("\n--- Reading #%u ---\n", sendCount);

    float tdsValue         = getTDS();
    float turbidityValue   = getTurbidity();
    float temperatureValue = getTemperature();

    Serial.println("  [SENSOR] Live readings:");
    Serial.printf("           TDS:         %.2f ppm\n",  tdsValue);
    Serial.printf("           Turbidity:   %.2f /100\n", turbidityValue);
    Serial.printf("           Temperature: %.2f °C  [hardcoded+jitter]\n", temperatureValue);

    int rssi = WiFi.RSSI();
    Serial.printf("  [NET] WiFi RSSI: %d dBm (%s)\n", rssi, rssiQuality(rssi));
    Serial.printf("  [NET] Local IP:  %s\n", WiFi.localIP().toString().c_str());

    sendData(tdsValue, turbidityValue, temperatureValue);
}


// ── TDS Sensor ───────────────────────────────────────────────────────
float getTDS() {
    int   samples = 30;
    float sum     = 0;

    for (int i = 0; i < samples; i++) {
        sum += analogRead(TDS_PIN);
        delay(5);
    }

    float avg     = sum / samples;
    float voltage = avg * (3.3 / 4095.0);

    // Cubic calibration curve (kept exactly from legacy code)
    float tds = (133.42 * voltage * voltage * voltage
               - 255.86 * voltage * voltage
               + 857.39 * voltage) * 0.5;

    return tds;
}


// ── Turbidity Sensor ─────────────────────────────────────────────────
float getTurbidity() {
    int   samples = 30;
    float sum     = 0;

    for (int i = 0; i < samples; i++) {
        sum += analogRead(TURBIDITY_PIN);
        delay(5);
    }

    float avg            = sum / samples;
    float voltage        = avg * (3.3 / 4095.0);
    float actualVoltage  = voltage * 2.0;   // compensate voltage divider

    // map() works on integers, so scale×100 as in legacy code
    float turbidity = map(actualVoltage * 100, 0, 300, 100, 0);

    return turbidity;
}


// ── Temperature (hardcoded + realistic jitter) ───────────────────────
float getTemperature() {
    // Produces gentle variation: ±(0–0.9 °C) in 0.1 °C steps
    // sendCount cycles 0–9 then resets, giving a smooth drift pattern
    float jitter = (sendCount % 10) * 0.1;

    // Alternate direction every 10 readings so it oscillates naturally
    if ((sendCount / 10) % 2 == 0) {
        return TEMP_BASE + jitter;
    } else {
        return TEMP_BASE + (0.9 - jitter);
    }
}


// ── HTTP POST ────────────────────────────────────────────────────────
void sendData(float tds, float turbidity, float temperature) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("[ERR] Skipping POST — WiFi not connected.");
        return;
    }

    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(8000);

    JsonDocument doc;
    doc["tds"]         = round(tds         * 100) / 100.0;
    doc["turbidity"]   = round(turbidity   * 100) / 100.0;
    doc["temperature"] = round(temperature * 100) / 100.0;

    String payload;
    serializeJson(doc, payload);

    Serial.printf("  [TX] POST → %s\n", SERVER_URL);
    Serial.printf("       Body: %s\n", payload.c_str());

    unsigned long t0      = millis();
    int           httpCode = http.POST(payload);
    unsigned long elapsed = millis() - t0;

    if (httpCode > 0) {
        Serial.printf("  [RX] HTTP %d  (%lu ms)\n", httpCode, elapsed);

        if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_CREATED) {
            Serial.println("  [OK] Backend accepted data ✓");
            String response = http.getString();
            if (response.length() > 0) {
                Serial.printf("       Response: %s\n", response.c_str());
            }
        } else {
            Serial.printf("  [WARN] Unexpected status: %d\n", httpCode);
        }
    } else {
        Serial.printf("  [ERR] POST failed: %s\n", http.errorToString(httpCode).c_str());
        Serial.println("        Check SERVER_URL, server running, and firewall.");
    }

    http.end();
}


// ── WiFi Connection ───────────────────────────────────────────────────
void connectWiFi() {
    Serial.printf("[INFO] Connecting to \"%s\"", WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 40) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    Serial.println();

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("[OK]  WiFi connected!");
        Serial.printf("      IP Address : %s\n", WiFi.localIP().toString().c_str());
        Serial.printf("      Gateway    : %s\n", WiFi.gatewayIP().toString().c_str());
        Serial.printf("      Signal     : %d dBm (%s)\n", WiFi.RSSI(), rssiQuality(WiFi.RSSI()));
    } else {
        Serial.println("[ERR] WiFi connection FAILED.");
        Serial.println("      Check SSID, password, and that the network is 2.4 GHz.");
    }
}


// ── RSSI Quality Helper ───────────────────────────────────────────────
const char* rssiQuality(int rssi) {
    if (rssi >= -50) return "Excellent";
    if (rssi >= -65) return "Good";
    if (rssi >= -75) return "Fair";
    if (rssi >= -85) return "Weak";
    return "Very Weak";
}