# EpiSense

An IoT and machine learning system that monitors environmental indicators such as turbidity, TDS, and temperature to detect conditions associated with infectious disease outbreaks. Sensor data is analyzed using ML models and visualized through a real-time dashboard for early risk detection.

## Tech Stack

- **Hardware:** ESP32 + TDS, turbidity, and temperature sensors
- **Backend:** Python, FastAPI, WebSocket
- **ML:** XGBoost trained on [Kaggle Water Potability Dataset](https://www.kaggle.com/datasets/adityakadiwal/water-potability)
- **Frontend:** React, TypeScript, Recharts, Vite


---

# System Architecture

The system follows a **layered IoT-AI architecture** that separates sensing, processing, and visualization components.

**Environmental Sensing Layer**
Sensors continuously measure environmental indicators associated with water contamination and disease spread, including turbidity, TDS, and temperature.

**Edge Device Layer**
An ESP32 microcontroller collects sensor readings and transmits the data via WiFi to the backend server through REST API requests.

**Backend Processing Layer**
A FastAPI server receives the incoming data and processes it using a trained machine learning model that evaluates environmental conditions and predicts potential disease risk indicators.

**Real-Time Communication Layer**
Prediction results and sensor values are broadcast to connected clients using WebSockets.

**Application Layer**
A React-based web dashboard visualizes live sensor data streams, predicted risk levels, and historical environmental trends.

System flow:

Sensors
↓
ESP32
↓ WiFi
REST API
↓
FastAPI Backend
↓
Machine Learning Model
↓
WebSocket Stream
↓
React Web Dashboard

---


# Research Foundations

The project is inspired by research in three key areas:

### Infectious Disease Surveillance

Public health systems traditionally rely on delayed laboratory reporting and manual surveillance mechanisms, which slow outbreak detection. 

### Environmental Indicators of Disease Spread

Environmental factors such as water contamination and environmental conditions are closely linked with diseases like cholera, typhoid, dengue, and malaria. 

### IoT-Based Monitoring Systems

IoT sensor networks allow continuous real-time monitoring of environmental conditions and provide valuable data streams for predictive analysis. 

### AI for Predictive Analytics

Machine learning models trained on environmental datasets can detect patterns that indicate increased disease risk conditions. 

---

# Key Features

Real-time environmental sensing using IoT sensors
Machine learning based outbreak risk prediction
Continuous environmental data collection
Real-time web dashboard visualization
Scalable architecture for future public health data integration

---

## License

MIT