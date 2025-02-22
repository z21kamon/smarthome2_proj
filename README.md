# SmartHome2 Project: Web App component

This repository contains the code and resources for a server app component of a smart home automation system developped during the *Учёные Будущего* Summer School, Krasnoyarsk, July-August 2020.

## Project Description

The **SmartHome2 Project** is a server-based smart home automation solution that integrates IoT devices to provide seamless control and monitoring of home systems. The server communicates with Arduino devices using the MQTT protocol, enabling it to receive data from sensors and control devices such as heaters, lights, and more. 

Additionally, the project includes a simple API for communication with an [Android app](https://github.com/roessss/smarthouse), allowing users to interact with the system remotely.

## Tech Stack

- **Backend**: Python, Django
- **IoT Integration**: MQTT protocol for communication with Arduino devices
- **Database**: PostgreSQL
- **API**: RESTful API for Android app communication

## Credits

This project was developed by [Iaroslav Prudnikov](https://github.com/z21kamon).

## Installation and Setup Guide

Follow these steps to set up the SmartHome2 Project on your local machine:

### Prerequisites
- Python 3.8 or higher
- PostgreSQL database
- Arduino devices with MQTT support

### Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/z21kamon/smarthome2_proj.git
   cd smarthome2_proj
   ```

2. **Set Up the Backend**:
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
   - Configure the database in the `smarthome2_proj/settings.py` file.
   - Run migrations:
     ```bash
     python manage.py migrate
     ```
   - Start the backend server:
     ```bash
     python manage.py runserver
     ```

3. **Connect to Arduino Devices**:
   - Ensure your Arduino devices are configured to use the MQTT protocol.
   - Update the MQTT broker settings in the backend configuration file to match your setup.

4. **Run the Application**:
   - The backend server will handle communication with Arduino devices and provide the API for the Android app.
