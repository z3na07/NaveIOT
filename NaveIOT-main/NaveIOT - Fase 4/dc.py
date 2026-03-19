# dc.py - Device Controller per Raspberry Pi Pico
import json
import time
import socket
import dht
from machine import Pin

# Importando picowifi, la Pico esegue automaticamente la connessione WiFi
# usando esattamente le tue funzioni originali scritte in quel file.
import picowifi

# Configurazione del PIN del sensore (Modifica se non è collegato al GP0)
PIN_DHT = 0

def leggi_configurazione():
    with open('da.json', 'r') as f:
        return json.load(f)

def leggi_sensore():
    sensor = dht.DHT11(Pin(PIN_DHT))
    try:
        sensor.measure()
        return sensor.temperature(), sensor.humidity()
    except Exception as e:
        print("Errore lettura sensore:", e)
        return 19.12, 64.20 # Valori simulati di fallback in caso di errore

def main():
    config_da = leggi_configurazione()
    ip_da = config_da['IP']
    porta_da = config_da['porta']
    invio_numero = 1

    while True:
        # 1. Lettura dati dal sensore
        temp, umid = leggi_sensore()
        
        # 2. Creazione payload come da "SEMPLIFICAZIONE" del PDF
        payload = {
            "cabina": 1,
            "ponte": 1,
            "temperaturam": float(temp),
            "umiditam": float(umid),
            "dataeora": time.time(),
            "invionumero": invio_numero,
            "identita": "GIOT-001"
        }
        
        dati_json = json.dumps(payload)
        
        # 3. DEBUG: Stampa del dato non criptato inviato
        print(f"[DC DEBUG] Dati non criptati inviati a {ip_da}:{porta_da} -> {dati_json}")
        
        # 4. Invio via Socket al DA (Gateway)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip_da, porta_da))
            s.sendall(dati_json.encode('utf-8'))
            s.close()
            invio_numero += 1
        except Exception as e:
            print(f"[DC ERRORE] Impossibile raggiungere il DA: {e}")
            
        time.sleep(5)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Esecuzione bloccata.")