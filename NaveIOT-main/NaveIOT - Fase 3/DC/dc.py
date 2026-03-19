import json
import time
import socket
import random

def init_led():
    try:
        import machine
        return machine.Pin("LED", machine.Pin.OUT)
    except Exception:
        class FakeLED:
            def value(self, v): pass
        return FakeLED()

try:
    import wifidc
    WiFi_WLAN = wifidc.connetti()
except Exception as e:
    print(f"[SIMULAZIONE PC] Avviso WiFi ignorato: {e}")

try:
    from misurazione import on_temperatura, on_umidita
except ImportError:
    def on_temperatura(decimali): return round(random.uniform(20.0, 30.0), decimali)
    def on_umidita(decimali): return round(random.uniform(40.0, 70.0), decimali)

def leggi_config(file_config):
    try:
        with open(file_config, "r", encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERRORE] Impossibile leggere {file_config}: {e}")
        return {}

def manda_dati(sock, dati, led):
    messaggio = json.dumps(dati)
    led.value(1)
    sock.sendall((messaggio + '\n').encode('utf-8'))
    time.sleep(0.1)
    led.value(0)

def main():
    led = init_led()
    led.value(0)

    config_dc = leggi_config("configurazionedc.json")
    config_da = leggi_config("da.json")
    
    if not config_dc or not config_da:
        return

    camera = config_dc.get("camera", "Sconosciuta")
    ponte = config_dc.get("ponte", "Sconosciuto")
    sensore = config_dc.get("sensore", "DHT22")
    identita = config_dc.get("identita", "DC-01")

    ip_server = config_da.get("IP", "127.0.0.1")
    porta_server = config_da.get("porta", 9090)

    contatore = 0

    print(f"[DC {identita}] Mi connetto al server DA {ip_server}:{porta_server}...")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip_server, porta_server))
        print(f"[DC {identita}] Connesso!")

        buffer = sock.recv(1024).decode('utf-8')
        if not buffer: return
            
        parametri = json.loads(buffer)
        tempo_attesa = parametri.get("TEMPO_RILEVAZIONE", 5)
        decimali = parametri.get("N_DECIMALI", 2)

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
            print(json.dumps(dato, indent=4, ensure_ascii=False))
            
            manda_dati(sock, dato, led)
            time.sleep(tempo_attesa)

    except ConnectionRefusedError:
        print(f"[DC {identita}] ERRORE: Il server {ip_server}:{porta_server} rifiuta la connessione.")
    except KeyboardInterrupt:
        # --- RIEPILOGO FINALE DC ---
        print("\n" + "="*40)
        print(f"CHIUSURA CLIENT DC ({identita})")
        print("="*40)
        print(f"Totale rilevazioni inviate al DA: {contatore}")
        print("="*40)
    except Exception as errore:
        print(f"[DC {identita}] Errore imprevisto: {errore}")
    finally:
        try:
            sock.close()
        except NameError:
            pass

if __name__ == "__main__":
    main()
