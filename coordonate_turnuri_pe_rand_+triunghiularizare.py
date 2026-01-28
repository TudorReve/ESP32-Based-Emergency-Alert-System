import machine
import time
import urequests
from machine import UART

uart = UART(2, baudrate=38400, tx=17, rx=16)


def triangulate_location(towers):
    """
    towers: listă de tuple (RSSI, lat, lon)
    Returnează o estimare (latitudine, longitudine) a locației dispozitivului.
    """
    if not towers:
        print("⚠️ Nu există date suficiente pentru triangulație.")
        return None

    sum_lat = 0.0
    sum_lon = 0.0
    weight_sum = 0.0

    for rssi, lat, lon in towers:
        # Convertim RSSI într-o pondere pozitivă: semnal mai puternic => pondere mai mare
        weight = max(1, 110 + rssi)  # Ex: RSSI = -80 => weight = 30
        sum_lat += lat * weight
        sum_lon += lon * weight
        weight_sum += weight

    estimated_lat = sum_lat / weight_sum
    estimated_lon = sum_lon / weight_sum

    return estimated_lat, estimated_lon

def send_at(cmd, delay=1, read_response=True):
    #print("📤 Sending:", cmd)
    uart.write((cmd + '\r\n').encode())
    time.sleep(delay)

    if read_response:
        response = b""
        timeout = time.time() + 2 # max 5 sec așteptare
        while time.time() < timeout:
            if uart.any():
                response += uart.read()
            else:
                time.sleep(0.1)
        
        try:
            decoded = response.decode(errors="ignore")
            print("📥 Raw response:", decoded)
            return decoded
        except:
            return ""
    return ""



def extract_ceng_info(data):
    results = []
    start = data.find("+CENG: ")

    while start != -1:
        end = data.find("\r\n", start)
        if end == -1:
            end = len(data)
        entry = data[start:end].strip()
        start = data.find("+CENG: ", end)

        #print("ENTRY RAW LINE:", entry)
        try:
            parts = entry.split('"')[1].split(',')
            #print("SPLIT PARTS:", parts)
        except IndexError:
            print("⚠️ Format incorect, skipping line")
            continue

        if len(parts) < 7 or "" in parts:
            continue

        try:
            index = int(entry.split(":")[1].split(",")[0])
            rssi = int(parts[1])

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

            cell_id_dec = int(cell_id_hex, 16)
            lac_dec = int(lac_hex, 16)

            results.append({
                "Index": index,
                "RSSI": rssi,
                "Cell_ID": cell_id_dec,
                "MCC": int(mcc),
                "MNC": int(mnc),
                "LAC": lac_dec
            })
        except (ValueError, IndexError):
            continue

    return results


def get_location_from_cell(cell_info):
    json_data = f'''
{{
  "token": "pk.bf6e9a0afa53bfeeefadc5822caf2a0d",
  "radio": "gsm",
  "mcc": {cell_info["MCC"]},
  "mnc": {cell_info["MNC"]},
  "cells": [{{"lac": {cell_info["LAC"]}, "cid": {cell_info["Cell_ID"]}}}],
  "address": 1
}}'''

    send_at(f'AT+HTTPDATA={len(json_data)},10000')
    send_at(json_data)
    send_at('AT+HTTPACTION=1',1)
    uart.write('AT+HTTPREAD\r\n')
    time.sleep(2)
    response = uart.read()
    response = response.decode('utf-8')
    
    return response


def get_data():
    # Activăm modul de debug CENG
    uart.write('AT+CENG=1\r\n')
    time.sleep_ms(100)
    uart.write('AT+CENG=2,1\r\n')
    time.sleep(1)
    uart.write('AT+CENG?\r\n')
    uart.write('AT+CENG=1\r\n')
    time.sleep_ms(100)
    response = uart.read()
    response = response.decode('utf-8')
    #print ("Raspuns CENG brut:",repr(response))
    
    # Conectare internet
    uart.write('AT+SAPBR=3,1,"Contype","GPRS"\r\n')
    time.sleep_ms(10)
    uart.write('AT+SAPBR=3,1,"APN","live.vodafone.com"\r\n')
    time.sleep_ms(10)
    uart.write('AT+SAPBR=1,1\r\n')
    time.sleep_ms(10)
    uart.write('AT+HTTPINIT\r\n')
    time.sleep_ms(500)
    uart.write('AT+HTTPPARA="CID",1\r\n')
    time.sleep_ms(250)
    uart.write('AT+HTTPSSL=1\r\n')
    time.sleep_ms(250)
    
    uart.write('AT+HTTPPARA="URL","https://eu1.unwiredlabs.com/v2/process.php"\r\n')
    time.sleep(1)
    uart.write('AT+HTTPPARA="CONTENT","application/json"\r\n')
    time.sleep(1)
    
    turnuri = []
    
    if response:
        #print("📡 Date CENG brute:\n", response)
        parsed = extract_ceng_info(response)
        
        if parsed:
            for entry in parsed:
                print(f"📶 RSSI: {entry['RSSI']}, MCC: {entry['MCC']}, MNC: {entry['MNC']}, LAC: {entry['LAC']}, Cell ID: {entry['Cell_ID']}")
            
                location = get_location_from_cell(entry)
                print("📍 Locație estimată:", location)
                
                try:
                    lat_start = location.find('"lat":') + len('"lat":')
                    lat_end = location.find(',', lat_start)
                    lat = float(location[lat_start:lat_end].strip())

                    lon_start = location.find('"lon":') + len('"lon":')
                    lon_end = location.find(',', lon_start)
                    lon = float(location[lon_start:lon_end].strip())

                    RSSI = int(int(entry['RSSI'])-110)
                    turnuri.append((RSSI ,lat, lon))
                except:
                    print("Nu s-au putut extrage cooronatele din raspuns!")
                    
        else:
            print("❌ Nu am găsit celule valide în datele primite.")
    else:
        print("❌ Nu s-au primit date de la modul GSM.")

    print ('\n')
    print ("Toate turnurile detectate:")
    for t in turnuri:
        print (" -", t)
    uart.write('AT+SAPBR=0,1\r\n')
    if turnuri:
        estimated_location = triangulate_location(turnuri)
    if estimated_location:
        print("\n📍 Poziție estimată prin triangulație:")
        print("   Lat:", estimated_location[0])
        print("   Lon:", estimated_location[1])
# Punctul de pornire
get_data()