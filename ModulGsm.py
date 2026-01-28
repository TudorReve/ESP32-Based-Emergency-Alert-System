import machine
import time
import urequests
import ujson
import re
from machine import UART, Pin

# Inițializare UART pe portul 2, cu baudrate 38400 și pinii TX și RX specificați
uart = UART(2, baudrate=38400, tx=17, rx=16)

# LED-uri (sau alți pini de semnalizare) pe GPIO 2 și 12
p2 = Pin(2, Pin.OUT)
p19 = Pin(12, Pin.OUT)

# Funcție pentru trimiterea unei comenzi AT și citirea răspunsului
def send_at(cmd, delay=1, read_response=True):
    print("📤 Sending:", cmd)
    uart.write((cmd + '\r\n').encode())
    time.sleep(delay)

    if read_response:
        response = b""
        timeout = time.time() + 3 
        while time.time() < timeout:
            if uart.any():
                response += uart.read()
                print(response)
            else:
                time.sleep(0.1)
        
        try:
            decoded = response.decode(errors="ignore")
            print("📥 Raw response:", decoded)
            return decoded
        except:
            return ""
    return ""

# Funcție pentru extragerea și decodificarea informațiilor celulare din răspunsul AT+CENG
def extract_ceng_info(data): 
    results = []
    start = data.find("+CENG: ")

    while start != -1:
        end = data.find("\r\n", start)
        if end == -1:
            end = len(data)
        entry = data[start:end].strip()
        start = data.find("+CENG: ", end)

        try:
            parts = entry.split('"')[1].split(',')
        except IndexError:
            print("⚠️ Format incorect, skipping line")
            continue

        # Ignorăm intrările incomplete sau invalide
        if len(parts) < 7 or "" in parts:
            continue

        try:
            index = int(entry.split(":")[1].split(",")[0])
            rssi = int(parts[1])

            # Index 0 este celula principală, restul sunt celule vecine
            if index == 0:
                if len(parts) < 10:
                    continue
                cell_id_hex = parts[6]
                mcc = parts[3]
                mnc = parts[4]
                lac_hex = parts[9]
            else:
                cell_id_hex = parts[3]
                mcc = parts[4]
                mnc = parts[5]
                lac_hex = parts[6]

            if any(p in ["", "ffff", "0000"] for p in [cell_id_hex, lac_hex, mcc, mnc]):
                continue

            # Convertim valorile hex în zecimal
            cell_id_dec = int(cell_id_hex, 16)
            lac_dec = int(lac_hex, 16)

            # Adăugăm datele valide în listă
            results.append({
                "Index": index,
                "RSSI": int(int(rssi)-110),
                "Cell_ID": cell_id_dec,
                "MCC": int(mcc),
                "MNC": int(mnc),
                "LAC": lac_dec
            })

            # Limităm la 6 celule
            if len(results) >= 6:
                break

        except (ValueError, IndexError):
            continue    

    return results

# Funcție care trimite datele celulare la UnwiredLabs și primește o locație estimată
def get_location_from_cell(cells_data):
    if not cells_data:
        print("❌ Nu s-au primit celule pentru localizare.")
        return None

    mcc = cells_data[0]['MCC']
    mnc = cells_data[0]['MNC']

    cell_entries = []
    for cell in cells_data:
        try:
            signal = int(cell["RSSI"])
            cell_entries.append({
                "lac": int(cell["LAC"]),
                "cid": int(cell["Cell_ID"]),
                "signal": signal
            })
        except Exception as e:
            print("⚠️ Eroare la procesarea unei celule:", e)

    if not cell_entries:
        print("❌ Nicio celulă validă pentru localizare.")
        return None

    # Construim payload JSON pentru API-ul UnwiredLabs
    json_payload = {
        "token": "pk.6f9929946edbdcb251a25b5efc6aac3f",
        "radio": "gsm",
        "mcc": int(mcc),
        "mnc": int(mnc),
        "cells": cell_entries,
        "address": 1
    }

    json_str = ujson.dumps(json_payload)
    print("📤 Trimitem JSON:\n", json_str)

    # Trimitem datele către modul GSM prin comenzi AT
    send_at(f'AT+HTTPDATA={len(json_str)},10000', 1) #Pregatim modulul pentru transferul HHTP
    time.sleep(1)
    uart.write(json_str+'\r\n')
    time.sleep(1)
    send_at('AT+HTTPACTION=1', 3) #Pornim protocolul HTTP
    uart.write('AT+HTTPREAD\r\n')
    time.sleep(4)

    # Citim răspunsul serverului
    response = uart.read()
    if response:
        response = response.decode('utf-8')
        return response
    else:
        print("❌ Nu s-a primit niciun răspuns de la server.")
        return None

# Funcție principală care citește datele celulare, se conectează la internet și trimite coordonatele
def get_data():
    # Activare raportare celule GSM
    uart.write('AT+CENG=1\r\n') #Activam enginering mode ul
    time.sleep_ms(100)
    uart.write('AT+CENG=2,1\r\n')#Cerem datele despre celule
    time.sleep(1)
    uart.write('AT+CENG?\r\n')
    uart.write('AT+CENG=1\r\n')#Oprim enginering mode ul
    time.sleep_ms(100)
    response = uart.read()
    response = response.decode('utf-8')
    print ("Raspuns CENG brut:",repr(response))

    # Inițializare conexiune GPRS
    uart.write('AT+SAPBR=3,1,"Contype","GPRS"\r\n')
    time.sleep_ms(10)
    uart.write('AT+SAPBR=3,1,"APN","live.vodafone.com"\r\n')
    time.sleep_ms(10)
    uart.write('AT+SAPBR=1,1\r\n') # Activăm GPRS ul
    time.sleep_ms(10)
    uart.write('AT+HTTPINIT\r\n') # Inițializăm serviciul HTTP 
    time.sleep_ms(500)
    uart.write('AT+HTTPPARA="CID",1\r\n') # Alegem conexiunea de date pe care să o folosim pentru HTTP (CID = 1)
    time.sleep_ms(1)
    uart.write('AT+HTTPSSL=1\r\n') # Activăm protocolul HTTPS
    time.sleep_ms(2)
    uart.write('AT+HTTPPARA="URL","https://eu1.unwiredlabs.com/v2/process.php"\r\n')
    time.sleep(1)
    uart.write('AT+HTTPPARA="CONTENT","application/json"\r\n')
    time.sleep(1)

    if response:
        parsed = extract_ceng_info(response)
        
        if parsed and len(parsed)>0:
            for entry in parsed:
                print(f"📶 RSSI: {entry['RSSI']}, MCC: {entry['MCC']}, MNC: {entry['MNC']}, LAC: {entry['LAC']}, Cell ID: {entry['Cell_ID']}")
            
            location = get_location_from_cell(parsed)
            print("📍 Locație estimată:\n", location)
                
            # Căutăm coordonatele GPS în răspunsul JSON
            try:
                lat_match = re.search(r'"lat":\s*([0-9.]+)', location)
                lon_match = re.search(r'"lon":\s*([0-9.]+)', location)

                if lat_match and lon_match:
                    lat = lat_match.group(1)
                    lon = lon_match.group(1)
                    google_maps_link = f"https://www.google.com/maps?q={lat},{lon}"
                    print("🗺 Link Google Maps:", google_maps_link)
                    
                    trimite_sms(google_maps_link,"+40775645665") # Tudor
                    time.sleep(3)
                else:
                    print("❌ Nu s-au putut extrage coordonatele din string.")
                    uart.write('AT+CFUN=1,1\r\n')  # Restart modem
            except Exception as e:
                print("⚠️ Eroare la parsarea coordonatelor:", e)
                
        else:
            print("❌ Nu am găsit celule valide în datele primite.")
            uart.write('AT+CFUN=1,1\r\n')
    else:
        print("❌ Nu s-au primit date de la modul GSM.")

    # Închidem conexiunea GPRS
    uart.write('AT+SAPBR=0,1\r\n')
    uart.read()

# Funcție pentru trimiterea unui SMS cu link-ul locației și puterea semnalului
def trimite_sms(mesaj, numar_telefon):
    uart.write('AT+CSQ\r\n')
    time.sleep(2)
    response = uart.read()
    if response:
        response = response.decode('utf-8')
    print(response)

    # Extragerea puterii semnalului
    if "+CSQ" in response:
        strength = response.split(":")[1].split(",")[0].strip()
        print("Signal Strength (RSSI):", strength)
    response = uart.read()
    if response:
        response = response.decode('utf-8').strip()
    print(response)

    try:
        print(f"📨 Trimit mesaj către {numar_telefon}...")

        # Modul text pentru SMS
        uart.write('AT+CMGF=1\r\n')
        time.sleep(1)

        # Trimitem către numărul dorit
        uart.write(f'AT+CMGS="{numar_telefon}"\r\n')
        time.sleep(1)
        
        # Mesaj + Ctrl+Z (char 26 = EOF)
        uart.write("AM NEVOIE DE AJUTOR!(Puterea Semnalului este): "+ strength + " " + mesaj + chr(26))
        time.sleep(3)

        print("✅ Mesaj trimis cu succes!")
    except Exception as e:
        print("❌ Eroare la trimiterea SMS-ului:", e)
