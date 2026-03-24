/*
 * EpiSense — ESP32 Connectivity Test Firmware
 *
 * Tests WiFi connectivity and backend reachability WITHOUT physical sensors.
 * Sends simulated/mock sensor data to verify the full communication pipeline.
 *
 * What this tests:
 *   ✓ WiFi association and IP assignment
 *   ✓ HTTP POST to backend server
 *   ✓ JSON serialization
 *   ✓ Server response parsing
 *   ✓ Reconnection logic
 *
 * NO hardware sensors required — all values are simulated.
 *
 * Libraries Required:
 *   - WiFi.h          (built-in ESP32)
 *   - HTTPClient.h    (built-in ESP32)
 *   - ArduinoJson.h   (install via Library Manager)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ── Configuration ───────────────────────────────────────────────────
// ⚠️  UPDATE THESE before flashing
const char* WIFI_SSID     = "Poison ";
const char* WIFI_PASSWORD = "Shaurya3003";

// ⚠️  UPDATE with your backend server IP/URL
// const char* SERVER_URL = "http://192.168.1.100:8000/api/sensor-data";
const char* SERVER_URL = "http://192.168.19.151:8000/api/sensor-data";

// How often to send a test POST (milliseconds)
const unsigned long SEND_INTERVAL = 10000;  // 10 seconds

// ── Mock Sensor Ranges ───────────────────────────────────────────────
// Simulated values cycle within realistic water quality ranges
const float TDS_BASE         = 250.0;   // ppm — typical tap water
const float TURBIDITY_BASE   = 2.5;     // NTU — fairly clear
const float TEMPERATURE_BASE = 24.0;    // °C  — room temperature water

// ── Timing ──────────────────────────────────────────────────────────
unsigned long lastSendTime = 0;
unsigned int  sendCount    = 0;


// ════════════════════════════════════════════════════════════════════
void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println();
    Serial.println("============================================");
    Serial.println("  EpiSense — WiFi + Backend Connectivity");
    Serial.println("               Test Mode");
    Serial.println("============================================");
    Serial.println("  [!] Sensors are SIMULATED — no hardware");
    Serial.println("      sensors required for this test.");
    Serial.println("============================================");
    Serial.println();

    connectWiFi();

    // Run one immediate test on boot so you don't wait 10 seconds
    Serial.println("[INFO] Running initial connectivity test...");
    runTest();
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

        runTest();
    }
}


// ── Main Test Cycle ─────────────────────────────────────────────────
void runTest() {
    sendCount++;
    Serial.printf("\n--- Test #%u ---\n", sendCount);

    // Generate mock sensor values with slight variation each cycle
    float mockTDS         = TDS_BASE         + (sendCount % 10) * 3.7;
    float mockTurbidity   = TURBIDITY_BASE   + (sendCount % 5)  * 0.4;
    float mockTemperature = TEMPERATURE_BASE + (sendCount % 8)  * 0.3;

    Serial.println("  [SIM] Simulated sensor readings:");
    Serial.printf("        TDS:         %.2f ppm\n", mockTDS);
    Serial.printf("        Turbidity:   %.2f NTU\n", mockTurbidity);
    Serial.printf("        Temperature: %.2f °C\n", mockTemperature);

    // Check WiFi signal quality
    int rssi = WiFi.RSSI();
    Serial.printf("  [NET] WiFi RSSI: %d dBm (%s)\n", rssi, rssiQuality(rssi));
    Serial.printf("  [NET] Local IP:  %s\n", WiFi.localIP().toString().c_str());

    // Attempt to POST to backend
    sendData(mockTDS, mockTurbidity, mockTemperature);
}


// ── WiFi Connection ─────────────────────────────────────────────────
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


// ── HTTP POST ───────────────────────────────────────────────────────
void sendData(float tds, float turbidity, float temperature) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("[ERR] Skipping POST — WiFi not connected.");
        return;
    }

    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(8000);  // 8-second timeout

    // Build JSON payload (identical structure to real firmware)
    JsonDocument doc;
    doc["tds"]         = round(tds         * 100) / 100.0;
    doc["turbidity"]   = round(turbidity   * 100) / 100.0;
    doc["temperature"] = round(temperature * 100) / 100.0;
    doc["test_mode"]   = true;   // Extra flag so the backend knows this is a test

    String payload;
    serializeJson(doc, payload);

    Serial.printf("  [TX] POST → %s\n", SERVER_URL);
    Serial.printf("       Body: %s\n", payload.c_str());

    unsigned long t0 = millis();
    int httpCode = http.POST(payload);
    unsigned long elapsed = millis() - t0;

    if (httpCode > 0) {
        Serial.printf("  [RX] HTTP %d  (%lu ms)\n", httpCode, elapsed);

        if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_CREATED) {
            Serial.println("  [OK] Backend reachable — data accepted ✓");
            String response = http.getString();
            if (response.length() > 0) {
                Serial.printf("       Response: %s\n", response.c_str());
            }
        } else {
            Serial.printf("  [WARN] Backend returned unexpected status: %d\n", httpCode);
        }
    } else {
        Serial.printf("  [ERR] POST failed: %s\n", http.errorToString(httpCode).c_str());
        Serial.println("        Check SERVER_URL, server is running, and firewall rules.");
    }

    http.end();
}


// ── RSSI Quality Helper ──────────────────────────────────────────────
const char* rssiQuality(int rssi) {
    if (rssi >= -50) return "Excellent";
    if (rssi >= -65) return "Good";
    if (rssi >= -75) return "Fair";
    if (rssi >= -85) return "Weak";
    return "Very Weak";
}
