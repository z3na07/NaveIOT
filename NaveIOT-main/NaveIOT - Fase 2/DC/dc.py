import json
import time
import socket
import os
from misurazione import on_temperatura, on_umidita

# Legge il file di configurazione
def leggi_config(file_config):
    f = open(file_config, "r")
    config = json.load(f)
    f.close()
    return config

# Manda i dati al server
def manda_dati(sock, dati):
    messaggio = json.dumps(dati)
    sock.sendall(messaggio.encode('utf-8') + b'\n')

# PROGRAMMA PRINCIPALE
cartella = os.path.dirname(__file__)
file_config = os.path.join(cartella, "configurazionedc.conf")

# Leggo la configurazione
config = leggi_config(file_config)

cabina = config["cabina"]
ponte = config["ponte"]
sensore = config["sensore"]
identita = config["identita"]

# Indirizzo del server (fisso)
ip_server = "127.0.0.1"
porta_server = 9999

contatore = 0

print(f"[DC {identita}] Mi connetto al server {ip_server}:{porta_server}...")

try:
    # Creo il socket e mi connetto
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip_server, porta_server))
    print(f"[DC {identita}] Connesso!")

    # Ricevo i parametri dal server
    messaggio = sock.recv(1024).decode('utf-8')
    parametri = json.loads(messaggio)
    tempo_attesa = parametri["TEMPO_RILEVAZIONE"]
    decimali = parametri["N_DECIMALI"]

    print(f"[DC {identita}] Tempo rilevazione: {tempo_attesa}s, Decimali: {decimali}")
    print(f"[DC {identita}] Inizio a mandare dati (CTRL+C per fermare)")

    # Ciclo infinito di invio dati
    while True:
        contatore = contatore + 1

        # Leggo temperatura e umidità
        temp = on_temperatura(decimali)
        umid = on_umidita(decimali)

        # Preparo il dato da mandare
        dato = {
            "cabina": cabina,
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

        # Mando il dato al server
        manda_dati(sock, dato)

        # Aspetto prima della prossima rilevazione
        time.sleep(tempo_attesa)

except KeyboardInterrupt:
    print(f"\n[DC {identita}] Fermato dall'utente")
except Exception as errore:
    print(f"[DC {identita}] Errore: {errore}")
finally:
    try:
        sock.close()
        print(f"[DC {identita}] Connessione chiusa")
    except:
        pass

print(f"\n[DC {identita}] -- FINE --")
print(f"[DC {identita}] Rilevazioni inviate: {contatore}")