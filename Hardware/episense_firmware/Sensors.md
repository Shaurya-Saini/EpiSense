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


---

## FINAL NOTES

* TDS gives approximate ppm values
* Turbidity is relative (0–100 scale)
* Both sensors are now safely connected to ESP32
* Can be extended later with temperature + ML
