import network
import time
import json

def connetti():
    with open('wifipico.json', 'r') as f:
        credenziali = json.load(f)
        
    ssid = credenziali.get('ssid', 'iot')
    pw = credenziali.get('pw', 'iotpassword')
        
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connessione in corso a", ssid)
        wlan.connect(ssid, pw)
        while not wlan.isconnected():
            print(".", end="")
            time.sleep(1)
            
    print("\nConnesso al WiFi!")
    print("Configurazione:", wlan.ifconfig())
    return wlan
