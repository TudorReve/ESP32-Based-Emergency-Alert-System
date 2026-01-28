import machine
import time
import urequests
import network

gsm = machine.UART(2, 9600)
API_KEY = "pk.75d863227eb8b117ce78c52e8b6233d0"
def connect_to_GPRS():
    """Connect to GPRS using SIM800C and initialize HTTP."""
    gsm.write(b'AT\r')  
    time.sleep(1)
    
    gsm.write('AT+SAPBR=3,1,"Contype","GPRS"\r')  
    time.sleep(1)
    
    gsm.write('AT+SAPBR=3,1,"APN","live.vodafone.com"\r')  
    time.sleep(1)
    
    gsm.write('AT+SAPBR=1,1\r')  
    time.sleep(3)  # Allow connection time
    
    # Verify GPRS is connected
    gsm.write('AT+SAPBR=2,1\r')  
    time.sleep(1)
    
    
    response = gsm.read()  
    print("raspunsul este:",response)

    
    


   
def extract_ceng_info(data):
    results = []
    start = data.find("+CENG: ")
    
    while start != -1:
        end = data.find("\r\n", start)
        if end == -1:
            end = len(data)
        entry = data[start:end].strip()
        start = data.find("+CENG: ", end)
        
        parts = entry.split('"')[1].split(',')

        if len(parts) < 7:
            continue
        
        index = int(entry.split(":")[1].split(",")[0])  # Extrag indicele CENG (0,1,2,3...)
        rssi = parts[1]  # Extrag RSSI-ul

        if index == 0:
            # Caz special pentru +CENG: 0 care are un format diferit
            cell_id_hex = parts[6]
            mcc = parts[3]
            mnc = parts[4]
            lac_hex = parts[9]
        else:
            # Format normal pentru +CENG: 1-6
            cell_id_hex = parts[3]
            mcc = parts[4]
            mnc = parts[5]
            lac_hex = parts[6]

        # Conversie din hex în decimal pentru Cell ID și LAC
        cell_id_dec = int(cell_id_hex, 16)
        lac_dec = int(lac_hex, 16)

        results.append({
            "Index": index,
            "RSSI": int(rssi),
            "Cell_ID": cell_id_dec,
            "MCC": int(mcc),
            "MNC": int(mnc),
            "LAC": lac_dec
        })

    return results

def get_cell_location(mcc, mnc, cell_id, lac):
    url = f"https://opencellid.org/cell/get?key={API_KEY}&mcc={mcc}&mnc={mnc}&lac={lac}&cellid={cell_id}&format=json"
    try:
        response = urequests.get(url)
        if response.status_code == 200:
            print("Exista conexiune la internet!")
            data = response.json()
            response.close()
            if "lat" in data and "lon" in data:
                return {
                    "Latitude": data["lat"],
                    "Longitude": data["lon"]
                }
            else:
                return {"Error": "Cell not found"}
        else:
            response.close()
            return {"Error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"Error": str(e)}
    
def get_data():
    gsm.write('AT\r')
    time.sleep(1)
    gsm.write('AT+CENG=1\r')
    time.sleep(1)
    gsm.write('AT+CENG=2,1\r')
    time.sleep(5)
    print("Datele urmeaza sa fie citite...")
    dataT = gsm.read()
    print("Datele au fost citite!")
    #print("Urmeaza conectarea la GPRS...")
    #connect_to_GPRS()
    if dataT:
        dataT = dataT.decode('utf-8')
        print("Datele GSM primite:", dataT)
        
        cell_entries = extract_ceng_info(dataT)
        
        for entry in cell_entries:
            location = get_cell_location(entry["MCC"], entry["MNC"], entry["Cell_ID"], entry["LAC"])
            print(f"RSSI: {entry['RSSI']}, MCC: {entry['MCC']}, MNC: {entry['MNC']}, LAC: {entry['LAC']}, Cell ID: {entry['Cell_ID']} -> {location}")
    else:
        print("Nu s-au primit date de la modem!")
connect_to_GPRS()        