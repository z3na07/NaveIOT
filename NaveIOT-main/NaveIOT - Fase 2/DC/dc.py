import json # Per gestire il formato dei dati JSON
import time # Per gestire le pause (sleep)
import socket # Per la comunicazione di rete
import os # Per gestire i percorsi dei file
from misurazione import on_temperatura, on_umidita # Importa le funzioni di simulazione

# Funzione per leggere il file di configurazione (JSON)
def leggi_config(file_config):
    f = open(file_config, "r") # Apre il file in modalità lettura
    config = json.load(f)      # Carica il contenuto JSON in un dizionario Python
    f.close()                  # Chiude il file
    return config              # Restituisce i dati

# Funzione per inviare i dati tramite il socket
def manda_dati(sock, dati):
    messaggio = json.dumps(dati) # Trasforma il dizionario in una stringa JSON
    # Invia i dati codificati in byte aggiungendo un a capo '\n' come separatore
    sock.sendall(messaggio.encode('utf-8') + b'\n')

# --- PROGRAMMA PRINCIPALE ---
cartella = os.path.dirname(__file__) # Ottiene la cartella dove si trova lo script
file_config = os.path.join(cartella, "configurazionedc.conf") # Crea il percorso del file config

config = leggi_config(file_config) # Legge la configurazione locale

# Leggo la configurazione
config = leggi_config(file_config)

# Estrae i dati dal file di configurazione
cabina = config["cabina"]
ponte = config["ponte"]
sensore = config["sensore"]
identita = config["identita"]

# Imposta i dati del server (localhost in questo caso)
ip_server = "127.0.0.1"
porta_server = 9999

contatore = 0 # Conta quante rilevazioni abbiamo fatto

print(f"[DC {identita}] Mi connetto al server {ip_server}:{porta_server}...")

try:
    # Crea il canale di comunicazione (Socket TCP)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip_server, porta_server)) # Si connette al server
    print(f"[DC {identita}] Connesso!")

    # Riceve dal server i parametri operativi (tempo di attesa e decimali)
    messaggio = sock.recv(1024).decode('utf-8')
    parametri = json.loads(messaggio)
    tempo_attesa = parametri["TEMPO_RILEVAZIONE"]
    decimali = parametri["N_DECIMALI"]

    print(f"[DC {identita}] Tempo rilevazione: {tempo_attesa}s, Decimali: {decimali}")
    print(f"[DC {identita}] Inizio a mandare dati (CTRL+C per fermare)")

    # Ciclo infinito per inviare dati periodicamente
    while True:
        contatore = contatore + 1 # Incrementa il numero di invii

        # Ottiene i valori simulati dai sensori
        temp = on_temperatura(decimali)
        umid = on_umidita(decimali)

        # Costruisce il pacchetto dati JSON
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

        # Stampa a video quello che sta per inviare, operazioe di debug
        print(f"\n[DC {identita}] Invio rilevazione {contatore}:")
        print(json.dumps(dato, indent=4))

        manda_dati(sock, dato) # Invia effettivamente i dati

        time.sleep(tempo_attesa) # Aspetta prima della prossima lettura

except KeyboardInterrupt: # Se l'utente preme CTRL+C
    print(f"\n[DC {identita}] Fermato dall'utente")
except Exception as errore: # Se c'è un errore generico
    print(f"[DC {identita}] Errore: {errore}")
finally: # In ogni caso, chiudo la connessione prima di terminare
    try:
        sock.close() # Chiude sempre la connessione alla fine
        print(f"[DC {identita}] Connessione chiusa")
    except:
        pass # Se la chiusura fallisce (magari perché già chiuso), non dirmi nulla e vai avanti

# Statistiche finali prima di chiudere lo script
print(f"\n[DC {identita}] -- FINE --")
print(f"[DC {identita}] Rilevazioni inviate: {contatore}")
