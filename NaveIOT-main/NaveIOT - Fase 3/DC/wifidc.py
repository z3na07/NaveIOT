import time
import json

# Tentiamo di importare network. Se fallisce, sappiamo di essere sul PC.
try:
    import network
    IS_MICROPYTHON = True
except ImportError:
    IS_MICROPYTHON = False

# Creiamo una finta classe WiFi per far felice il programma sul PC
class FintoWLAN:
    def active(self, stato):
        pass
        
    def isconnected(self):
        return True
        
    def connect(self, ssid, pw):
        pass
        
    def ifconfig(self):
        return ('127.0.0.1', '255.255.255.0', '192.168.1.1', '8.8.8.8')

def connetti():
    try:
        with open('wifipico.json', 'r', encoding='utf-8') as f:
            credenziali = json.load(f)
    except FileNotFoundError:
        print("[AVVISO] File 'wifipico.json' non trovato. Uso credenziali di default.")
        credenziali = {}
    except json.JSONDecodeError:
        print("[ERRORE] Il file 'wifipico.json' è corrotto. Uso credenziali di default.")
        credenziali = {}
        
    ssid = credenziali.get('ssid', 'iot')
    pw = credenziali.get('pw', 'iotpassword')
        
    if not IS_MICROPYTHON:
        print(f"[SIMULAZIONE PC] Modulo 'network' assente. Simulo la connessione alla rete '{ssid}'.")
        return FintoWLAN()
        
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connessione in corso a", ssid)
        wlan.connect(ssid, pw)
        while not wlan.isconnected():
            print(".", end="", flush=True)  # Aggiunto flush=True per stampare i puntini in tempo reale
            time.sleep(1)
            
    print("\nConnesso al WiFi!")
    print("Configurazione:", wlan.ifconfig())
    return wlan

# Piccolo test se esegui questo file singolarmente
if __name__ == "__main__":
    connetti()
