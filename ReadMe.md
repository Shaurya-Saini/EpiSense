# EpiSense: An IoT-AI Unified Outbreak Surveillance Platform

EpiSense is an advanced epidemiological surveillance system that bridges the gap between **autonomous environmental sensing** and **human clinical symptom reporting**. By fusing real-time water quality metrics (IoT) with time-decayed clinical data (Syndromic Surveillance) into a single geospatial **Outbreak Risk Index (ORI)**, EpiSense provides health authorities with early-warning capabilities for waterborne and vector-borne diseases.

---

## 🔬 Research & Biological Foundations

Traditional public health surveillance suffers from immense temporal lag due to its reliance on laboratory-confirmed diagnoses. EpiSense circumvents this latency by functioning as an **Early Warning System (EWS)** that triggers off leading indicators. 

### 1. Environmental Determinants of Health
Contamination of ground and surface water represents a direct vector for diseases like Cholera and Typhoid. The system continuously polls:
- **Total Dissolved Solids (TDS) & Turbidity**: High particulate matter serves as a physical reservoir and shield for pathogens.
- **Ambient Water Temperature**: Elevated temperatures logarithmically accelerate microbial replication and vector breeding cycles (e.g., *Aedes* and *Anopheles* mosquitoes).

### 2. Syndromic Surveillance
By observing clinical presentation (Fever, Diarrhea, Rash) before laboratory confirmation, the system captures localized symptomatic spikes. When these clinical clusters physically overlap with environmental degradation zones, the statistical confidence of an impending outbreak increases profoundly.

---

## 🧮 The Outbreak Risk Index (ORI) Architecture

The core of EpiSense is the **Unified Outbreak Risk Index**, a bounded scalar `[0.0, 1.0]` that dynamically calculates the severity of spatial health risks.

### The Fusion Equation
The ORI is a weighted additive model integrating the Environmental Score ($E_{score}$) and the Symptomatic Score ($S_{score}$):

$$ ORI_{zone} = (\alpha \times E_{score}) + (\beta \times S_{score\_decayed}) $$

*(Default Hyperparameters: $\alpha = 0.55$, $\beta = 0.45$)*

#### 1. Environmental Score ($E_{score}$)
The $E_{score}$ is derived by passing the real-time IoT array data (`TDS`, `Turbidity`, `Temp`) through an **XGBoost Classifier**. The model is trained on historical water potability datasets. The $E_{score}$ directly maps to the model's output contamination probability class.

#### 2. Symptomatic Score ($S_{score}$)
Upon a clinic logging a symptom cluster, a normalized symptomatic burden is calculated based on epidemiological relevance weights:

$$ Raw_{burden} = 0.4(Fever) + 0.35(Diarrhea) + 0.15(Vomiting) + 0.05(Rash) + 0.05(Respiratory) $$
$$ S_{score\_initial} = \min\left(\frac{Raw_{burden}}{Population_{zone}}, 1.0\right) $$

#### 3. Temporal Decay Function
Clinical reports inherently lose predictive value over time. Thus, the $S_{score}$ experiences continuous exponential decay governed by λ (decay constant, default $\lambda = 0.03 \approx 23h$ half-life).

$$ S_{score\_decayed} = S_{score\_initial} \times e^{-\lambda t} $$
*(Where $t$ = hours since report submission)*

---

## 🧬 Disease Inference Engine & Tiered Alerting

When a zone's ORI traverses defined thresholds, the **Disease Inference Engine** evaluates a heuristic matrix mapping environmental states and symptom flags to known pathogenic profiles.

- **Advisory ($\ge 0.4$)**: Low-level continuous monitoring required.
- **Warning ($\ge 0.6$)**: Statistically significant deviations. Clinic administrators in overlapping zones are preemptively notified.
- **Critical ($\ge 0.8$)**: Extreme multi-modal correlation (e.g., High Turbidity + High Diarrhea count). Triggers external emergency webhooks and advises immediate local intervention.

---

## 💻 Technical Stack

### Hardware (Edge Layer)
- **ESP32 Microcontroller**: Serves as the localized IoT network node.
- **Sensor Array**: Analog TDS, Analog Turbidity, Digital DS18B20 (OneWire).
- **Communication Protocol**: HTTP POST JSON payloads over WiFi `802.11 b/g/n`.

### Backend (Processing & Model Layer)
- **Framework**: Python 3.10+, FastAPI
- **Machine Learning**: `scikit-learn`, `xgboost` (Binary Classification, Potability Mapping).
- **State Management**: Thread-safe in-memory deques partitioning time-series data spatially by `zone_id`.
- **Stream**: Asynchronous WebSocket broadcasting of the `ZoneUpdate` schema.

### Frontend (Geospatial Visualization Layer)
- **Framework**: React 19, Vite, TypeScript.
- **Routing**: `react-router-dom` segregating the Global Dashboard from the Restricted Clinical Portal.
- **GIS**: `leaflet`, `react-leaflet`, and `leaflet.heat`. Renders an interactive WebGL-backed thermal map interpolating zone-specific ORIs.
- **UI/UX**: Extensive utilization of modern CSS Glassmorphism, CSS variables, CSS grid layouts, and active frame hardware acceleration for real-time charting (`recharts`).

---
