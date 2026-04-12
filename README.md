# CureConnect - Smart Healthcare Ecosystem 🏥💊

CureConnect is an integrated IoT solution designed to help elderly patients manage their medication schedules efficiently and safely. The system combines a smart physical organizer with a real-time web dashboard.

## 🚀 Features

- **8-Drawer Smart Dispenser:** Remote-controlled medication drawers via ESP32.
- **Real-time Dashboard:** Built with Flask and Firebase to monitor and control the device from anywhere.
- **SOS Emergency System:** A wearable bracelet that triggers immediate alerts and phone calls to family members.
- **GPS Tracking:** Live location monitoring using Google Maps API integration.
- **AI Voice Assistant:** Automated voice alerts to remind patients to take their medicine.
- **Patient Info Management:** Secure storage for medical records, blood types, and chronic conditions.

## 🛠️ Tech Stack

- **Frontend:** HTML5, Tailwind CSS, JavaScript (ES6+).
- **Backend:** Python (Flask).
- **Database:** Firebase Realtime Database.
- **Hardware:** ESP32, Servo Motors, GPS Module, SOS Button.
- **Deployment:** Vercel.

## 📂 Project Structure

```text
├── Web_App/
│   ├── static/          # CSS, JS, and Images
│   ├── templates/       # HTML Dashboards (Login, Dashboard)
│   ├── app.py           # Main Flask Server
│   └── firebase_config.py # Secure Firebase Initialization
├── Firmware/            # MicroPython code for ESP32
├── vercel.json          # Deployment configuration
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
