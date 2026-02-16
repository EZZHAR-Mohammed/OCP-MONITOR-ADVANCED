

````markdown
# Intelligent Industrial Monitoring System (OPC UA)

## 📌 Description
This project is an intelligent industrial supervision system based on OPC UA.  
It connects dynamically to OPC UA simulation servers, automatically discovers data, monitors industrial signals in real time, detects anomalies, manages alerts, and provides a modern web-based dashboard for decision support.

---

## 🚀 Main Features
- Dynamic connection to any OPC UA simulation server
- Automatic discovery of OPC UA variables
- Real-time data monitoring
- Intelligent anomaly detection
- Alert management and acknowledgment
- Historical data storage
- Modular and extensible architecture
- Secure and interoperable communication

---

## 🏗️ System Architecture
The system follows a modular architecture composed of:

- **OPC UA Server (external)**: Simulation or industrial server exposing data
- **OPC UA Connector**: Generic client for data acquisition
- **Intelligent Engine**: Data analysis and anomaly detection
- **Backend API**: Data access and real-time communication
- **Web Interface**: Visualization and supervision dashboard

---

## 🛠️ Technologies Used
- Python 3
- OPC UA (Client)
- FastAPI
- WebSocket
- SQLite / PostgreSQL
- JavaScript (Frontend)
- HTML / CSS

---

## 📋 Prerequisites
- Python 3.10 or higher
- OPC UA Simulation Server (e.g. Prosys OPC UA Simulation Server)
- UAExpert (optional, for testing OPC UA connections)

---

## ⚙️ Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/your-repository.git
````

2. Navigate to the backend folder:

   ```bash
   cd backend
   ```
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
4. Configure the OPC UA endpoint in the configuration file.
5. Run the application:

   ```bash
   python main.py
   ```

---

## 🔧 Configuration

The OPC UA connection parameters are defined in a configuration file:

* Server endpoint
* Security mode
* Authentication parameters (optional)

This allows easy connection to different OPC UA servers without code modification.

---

## ▶️ Usage

1. Start the OPC UA simulation server.
2. Launch the backend application.
3. Open the web interface.
4. Monitor real-time data, alerts, and system status.

---

## 🧪 Testing

The system was tested using:

* OPC UA simulation servers
* Real-time data acquisition scenarios
* Anomaly and alert triggering scenarios
* Connection loss and recovery tests

---

## 🔐 Security

* OPC UA secure communication supported
* Certificate-based security (optional)
* User access control at application level

---

## 🔮 Future Improvements

* Advanced machine learning for predictive maintenance
* Support for additional industrial protocols (MQTT, Modbus)
* Cloud deployment
* Digital Twin integration

---

## 👤 Author

**Mohamed EZZHAR**
Master’s Degree Project
Academic Year: 2025–2026

```


