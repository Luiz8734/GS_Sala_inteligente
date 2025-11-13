# FiapSense Dashboard

## Description

FiapSense is an innovative solution designed to monitor and optimize environmental conditions in corporate and educational settings. The project addresses the challenges posed by inadequate temperature, lighting, and noise levels, which can significantly impact well-being, productivity, and concentration. By leveraging real-time sensor data, FiapSense provides insights and alerts to create healthier and more productive environments.

## Problem Statement

In many workplaces and educational institutions, environmental factors such as temperature, humidity, luminosity, and noise levels are often overlooked. These factors can lead to discomfort, reduced productivity, and even health issues. FiapSense aims to tackle these challenges by providing a comprehensive monitoring system that ensures optimal conditions for users.

## Solution

FiapSense utilizes a combination of Arduino sensors and a Flask-based web application to monitor environmental conditions. The system collects data from various sensors, processes it, and displays it on a user-friendly dashboard. Users receive real-time updates and alerts, enabling them to take necessary actions to maintain a comfortable environment.

## Usage Instructions

1. **Clone the Repository**:
   ```
   git clone https://github.com/yourusername/fiap-sense-dashboard.git
   cd fiap-sense-dashboard
   ```

2. **Set Up the Environment**:
   - Create a virtual environment:
     ```
     python -m venv venv
     source venv/bin/activate  # On Windows use `venv\Scripts\activate`
     ```
   - Install the required dependencies:
     ```
     pip install -r requirements.txt
     ```

3. **Run the Backend Server**:
   ```
   python src/server.py
   ```

4. **Upload the Arduino Sketch**:
   - Open `src/arduino/fiap_sense.ino` in the Arduino IDE.
   - Upload the sketch to your Arduino board.

5. **Access the Dashboard**:
   - Open your web browser and navigate to `http://localhost:5000`.

## Replication Instructions

To replicate the setup online, you can use the Wokwi simulation for the Arduino project. The link to the simulation can be found in the `docs/WOKWI_LINK.txt` file.

## Links

- [Wokwi Simulation](docs/WOKWI_LINK.txt)
- [Explanatory Video](docs/VIDEO_LINK.txt)

## Technical Explanation

### MQTT and HTTP Endpoints

- **MQTT**: The project uses MQTT for real-time communication between the Arduino sensors and the Flask backend. The Arduino publishes sensor data to specific topics, which the MQTT client in `src/mqtt_client.py` subscribes to. This allows for efficient data transfer and low latency.

- **HTTP Endpoints**: The Flask application defines several API endpoints in `src/api.py` that handle requests for sensor data. These endpoints allow the frontend to fetch the latest sensor readings and display them on the dashboard.

## Source Code Files

- **Arduino Sketch**: `src/arduino/fiap_sense.ino`
- **Backend Server**: `src/server.py`
- **API Endpoints**: `src/api.py`
- **MQTT Client**: `src/mqtt_client.py`
- **HTML Template**: `templates/index.html`
- **CSS Styles**: `static/style.css`
- **JavaScript Logic**: `static/app.js`

## Team Members

- Luiz M.
- [Add other team members here]

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.