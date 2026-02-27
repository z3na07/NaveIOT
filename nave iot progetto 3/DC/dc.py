import json
import time
import socket

def init_led():
    try:
        import machine
        return machine.Pin("LED", machine.Pin.OUT)
    except Exception:
        class FakeLED:
            def value(self, v): pass
        return FakeLED()

# Importa wifidc (necessario per Pico W)
try:
    import wifidc
    WiFi_WLAN = wifidc.connetti()
except Exception as e:
    print("Avviso WiFi o simulazione su PC:", e)

from misurazione import on_temperatura, on_umidita

def leggi_config(file_config):
    with open(file_config, "r") as f:
        return json.load(f)

def manda_dati(sock, dati, led):
    messaggio = json.dumps(dati)
    led.value(1) # Accendi LED prima di inviare
    sock.sendall(messaggio.encode('utf-8') + b'\n')
    time.sleep(0.1) # Breve attesa per visualizzare il led
    led.value(0) # Spegni LED dopo invio

# PROGRAMMA PRINCIPALE
led = init_led()
led.value(0)

config_dc = leggi_config("configurazionedc.json")
config_da = leggi_config("da.json")

camera = config_dc["camera"]
ponte = config_dc["ponte"]
sensore = config_dc["sensore"]
identita = config_dc["identita"]

ip_server = config_da["IP"]
porta_server = config_da["porta"]

contatore = 0

print(f"[DC {identita}] Mi connetto al server DA {ip_server}:{porta_server}...")

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip_server, porta_server))
    print(f"[DC {identita}] Connesso!")

    messaggio = sock.recv(1024).decode('utf-8')
    parametri = json.loads(messaggio)
    tempo_attesa = parametri["TEMPO_RILEVAZIONE"]
    decimali = parametri["N_DECIMALI"]

    while True:
        contatore += 1
        temp = on_temperatura(decimali)
        umid = on_umidita(decimali)

        dato = {
            "camera": camera,
            "ponte": ponte,
            "sensore": sensore,
            "identita": identita,
            "osservazione": {
                "rilevazione": contatore,
                "temperatura": temp,
                "umidita": umid
            }
        }

        print(f"\n[DC {identita}] Invio rilevazione {contatore}:")
        print(json.dumps(dato, indent=4))
        
        manda_dati(sock, dato, led)
        time.sleep(tempo_attesa)

except KeyboardInterrupt:
    print(f"\n[DC {identita}] Fermato dall'utente")
except Exception as errore:
    print(f"[DC {identita}] Errore: {errore}")