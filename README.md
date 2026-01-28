# ESP32-Based-Emergency-Alert-System

# Danger-Alert-System

This intelligent safety device integrates an ESP32, SIM800C GSM module, microphone, SD card, accelerometer, push button, and LED indicators to detect and respond to emergencies. It features offline voice recognition using pre-recorded samples stored on an SD card, allowing it to recognize the keyword "ajutor" (help). The system also monitors for sudden impacts using an accelerometer or manual triggers via a button.

Upon detecting an emergency—through voice, crash, or button press—it activates the GSM module to connect to nearby cell towers, retrieving MCC, MNC, LAC, Cell ID, and RSSI values. This data is sent to the Unwired Labs API, which returns an estimated location using cell tower triangulation. A Google Maps link to the location is then sent via SMS to a predefined emergency contact. The system also allows sending a custom alert message or optionally contacting emergency services (112).

---

## 📷 Project Images

> The following images illustrate the system structure, alerts, and testing stages.

### 🔧 Device, Alerts & Testing

| Danger Alert Device                                 | Primire Mesaj                         |
| --------------------------------------------------- | ------------------------------------- |
| ![Danger Alert Device](danger%20alert%20device.jpg) | ![Primire Mesaj](primire%20mesaj.jpg) |

| Test Margine Piatra Neamt                                         | Prezentare Concurs                              |
| ----------------------------------------------------------------- | ----------------------------------------------- |
| ![Test Margine Piatra Neamt](test%20margine%20piatra%20neamt.jpg) | ![Prezentare Concurs](prezentare%20concurs.jpg) |

### 👥 Team / Assembly

| Colegi                      |
| --------------------------- |
| ![Colegi](colegi%20mei.jpg) |

---

## 📂 Repository Structure (to be expanded)

```
/ESP32-Based-Emergency-Alert-System
│── images/
│── src/
│── docs/
│── README.md
```

> Additional folders with source code and `.txt` files will be added progressively.
