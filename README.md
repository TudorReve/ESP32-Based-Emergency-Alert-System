# ESP32-Based-Emergency-Alert-System

# Danger-Alert-System

This intelligent safety device integrates an ESP32, SIM800C GSM module, microphone, SD card, accelerometer, push button, and LED indicators to detect and respond to emergencies. It features offline voice recognition using pre-recorded samples stored on an SD card, allowing it to recognize the keyword "ajutor" (help). The system also monitors for sudden impacts using an accelerometer or manual triggers via a button.

Upon detecting an emergency—through voice, crash, or button press—it activates the GSM module to connect to nearby cell towers, retrieving MCC, MNC, LAC, Cell ID, and RSSI values. This data is sent to the Unwired Labs API, which returns an estimated location using cell tower triangulation. A Google Maps link to the location is then sent via SMS to a predefined emergency contact. The system also allows sending a custom alert message or optionally contacting emergency services (112).

---

## 📑 Table of Contents

* [📷 Project Images](#-project-images)

  * [🔧 Device, Alerts & Testing](#-device-alerts--testing)
  * [👥 Team, Assembly & Presentation](#-team-assembly--presentation)

* [📄 TXT Documentation & Logs](#-txt-documentation--logs)

* [🐍 Python Scripts](#-python-scripts)

* [📷 Project Images](#-project-images)

  * [🔧 Device, Alerts & Testing](#-device-alerts--testing)
  * [👥 Team, Assembly & Presentation](#-team-assembly--presentation)

* [📂 Repository Structure](#-repository-structure-to-be-expanded)

---

## 📷 Project Images

> The following images illustrate the system structure, alerts, testing stages, and project presentation.

### 🔧 Device, Alerts & Testing

| Danger Alert Device                                 | Test Margine Piatra Neamt                                                                    | Primire Mesaj                         |
| --------------------------------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------- |
| ![Danger Alert Device](danger%20alert%20device.jpg) | <img src="test%20margine%20piatra%20neamt.jpg" alt="Test Margine Piatra Neamt" width="450"/> | ![Primire Mesaj](primire%20mesaj.jpg) |

### 👥 Team, Assembly & Presentation

| Colegi                      | Prezentare Concurs                              |
| --------------------------- | ----------------------------------------------- |
| ![Colegi](colegi%20mei.jpg) | ![Prezentare Concurs](prezentare%20concurs.jpg) |

---

## 📄 TXT Documentation & Logs

The following `.txt` files contain documentation, tests, and raw data related to GSM communication, sensors, and messaging:

* `accelerometer.txt` – Code used to calibrate and configure the accelerometer, preparing it for impact detection and motion monitoring.
* `message (3).txt` – Code responsible for configuring the GSM module to send messages and communicate with the external location API.
* `modul_gsm_comenzi.txt` – A collection of basic AT commands used for controlling and communicating with the SIM800 GSM module.
* `coordonate_turnuri_pe_rand_+_triunghiularizare.txt` – Logic for extracting coordinates from each detected cell tower and applying signal triangulation to estimate the device location.
* `SIM800_Series_GSM_Location_Application_Note.txt` – Official manufacturer documentation for the SIM800C module, describing GSM location features and usage guidelines.

---

## 🐍 Python Scripts

Python scripts used for testing GSM connectivity, internet access, and data processing:

* `ModulGsm.py` – Python implementation of GSM communication logic, used to test message handling and interaction with GSM services.
* `test_internet.py` – Script used to verify internet connectivity and data transmission before integrating the logic on the ESP32.

> These scripts are used for GSM communication testing, data extraction, and validation before ESP32 integration.
