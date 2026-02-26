import json
import socket
import time
import os
import signal
import sys
from datetime import datetime
import cripta # Importa il modulo di cifratura locale

# Variabili globali per tenere traccia dello stato del server
numero_invii = 0
dati_ricevuti = {}  # Dizionario che salva temporaneamente i dati di ogni cabina

# Legge le impostazioni generali del server
def leggi_parametri(file_parametri):
    f = open(file_parametri, "r")
    parametri = json.load(f)
    f.close()
    return parametri

# Scrive i dati finali nel file di "database"
def salva_dati(dati, file_archivio):
    # Apre in modalità "append" (aggiunge in coda) con codifica UTF-8
    f = open(file_archivio, "a", encoding='utf-8')
    # Scrive il JSON su una nuova riga
    f.write(json.dumps(dati, ensure_ascii=False) + "\n")
    f.close()

# Calcola le medie e "invia" alla piattaforma IoT
def manda_a_iotplatform(parametri, file_archivio):
    global numero_invii, dati_ricevuti
    
    if len(dati_ricevuti) == 0: # Se non abbiamo ricevuto nulla, non facciamo nulla
        return
    
    numero_invii = numero_invii + 1 # Incrementa il numero di aggregazioni fatte
    decimali = parametri["N_DECIMALI"]
    id_gateway = parametri["IDENTITA_GIOT"]
    
    lista_elaborati = [] # Conterrà i dati mediati per ogni cabina
    
    # Per ogni DC che ha inviato dati in questo intervallo di tempo
    for id_dc in dati_ricevuti:
        rilevazioni = dati_ricevuti[id_dc]
        
        if len(rilevazioni) == 0: continue
        
        # Calcolo la media matematica delle temperature ricevute
        somma_temp = sum(r["temperatura"] for r in rilevazioni)
        media_temp = round(somma_temp / len(rilevazioni), decimali)
        
        # Calcolo la media delle umidità
        somma_umid = sum(r["umidita"] for r in rilevazioni)
        media_umid = round(somma_umid / len(rilevazioni), decimali)
        
        # Prendo le informazioni fisse (cabina, ponte) dal primo pacchetto
        prima = rilevazioni[0]
        
        # Creo il blocco dati "elaborato"
        elaborato = {
            "cabina": prima["cabina"],
            "ponte": prima["ponte"],
            "sensore": prima["sensore"],
            "identita": prima["identita"],
            "elaborazione": {
                "mediatemperatura": media_temp,
                "mediaumidita": media_umid,
                "numerorilev": len(rilevazioni)
            }
        }
        lista_elaborati.append(elaborato)
    
    # Costruisco il pacchetto finale da inviare all'IOTP
    dato_finale = {
        "idgateway": id_gateway,
        "invionumero": numero_invii,
        "timestamp": datetime.now().isoformat(), # Data e ora corrente
        "dati": lista_elaborati
    }
    
    # Simulazione della cifratura richiesta dalla consegna
    dato_json = json.dumps(dato_finale, ensure_ascii=False)
    dato_criptato = cripta.criptazione(dato_json)
    
    # Salva il dato (per la simulazione salviamo quello leggibile)
    salva_dati(dato_finale, file_archivio)
    
    print(f"\n[DA] === INVIO {numero_invii} ALL'IOTPLATFORM ===")
    print(json.dumps(dato_finale, indent=4, ensure_ascii=False))
    
    dati_ricevuti.clear() # Svuota la memoria per il prossimo intervallo

# Funzione che gestisce la comunicazione con un singolo DC
def gestisci_dc(connessione, indirizzo, parametri):
    global dati_ricevuti
    print(f"[DA] Nuovo DC connesso: {indirizzo}")
    
    try:
        # Invia subito al DC quanto spesso deve misurare e con quanti decimali
        config_per_dc = {
            "TEMPO_RILEVAZIONE": parametri["TEMPO_RILEVAZIONE"],
            "N_DECIMALI": parametri["N_DECIMALI"]
        }
        connessione.sendall(json.dumps(config_per_dc).encode('utf-8'))
        
        buffer = "" # Contenitore per i dati che arrivano "a pezzi"
        while True:
            dati = connessione.recv(4096) # Riceve pacchetti di max 4KB
            if not dati: break # Se il DC si disconnette, esce dal ciclo
            
            buffer += dati.decode('utf-8')
            
            # Se nel buffer c'è un '\n', significa che abbiamo ricevuto almeno un messaggio completo
            while '\n' in buffer:
                messaggio, buffer = buffer.split('\n', 1)
                print(f"[DEBUG] Ho ricevuto questo: {messaggio}")
                try:
                    dato = json.loads(messaggio) # Converte in dizionario
                    id_dc = dato["identita"]
                    
                    # Salva la rilevazione nella lista corretta in base all'ID del DC
                    if id_dc not in dati_ricevuti:
                        dati_ricevuti[id_dc] = []
                    
                    dati_ricevuti[id_dc].append({
                        "cabina": dato["cabina"],
                        "ponte": dato["ponte"],
                        "sensore": dato["sensore"],
                        "identita": dato["identita"],
                        "temperatura": dato["osservazione"]["temperatura"],
                        "umidita": dato["osservazione"]["umidita"]
                    })
                except:
                    print("[DA] Errore decodifica messaggio")
    except Exception as e:
        print(f"[DA] Errore con {indirizzo}: {e}")
    finally:
        connessione.close() # Chiude la connessione specifica

# Funzione chiamata quando si preme CTRL+C
def quando_premo_ctrlc(sig, frame):
    # Calcoliamo il totale delle rilevazioni ancora presenti nel buffer
    # sommando la lunghezza di ogni lista di rilevazioni nel dizionario
    rilevazioni_residue = sum(len(lista) for lista in dati_ricevuti.values())
    
    print("\n" + "="*30)
    print("--- RIEPILOGO FINALE ---")
    print(f"Aggregazioni inviate all'IoTPlatform: {numero_invii}")
    print(f"Rilevazioni totali ricevute nell'ultima sessione: {rilevazioni_residue}")
    print("="*30)
    print("[DA] Server spento correttamente.")
    sys.exit(0)

# Punto di ingresso del programma
def main():
    signal.signal(signal.SIGINT, quando_premo_ctrlc) # Collega CTRL+C alla funzione sopra
    
    # Caricamento configurazioni iniziali
    cartella = os.path.dirname(__file__)
    parametri = leggi_parametri(os.path.join(cartella, "parametri.conf"))
    
    # Estrazione parametri di rete e tempo
    ip = parametri["IP_SERVER"]
    porta = parametri["PORTA_SERVER"]
    tempo_invio_secondi = parametri["TEMPO_INVIO"] * 60 # Converte minuti in secondi
    
    file_iotdata = os.path.join(os.path.dirname(cartella), "IOTP", "iotdata.dbt")
    
    # Creazione del Server Socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permette il riavvio immediato
    server.bind((ip, porta)) # Lega il server all'indirizzo e porta
    server.listen(5) # Si mette in ascolto di max 5 connessioni in coda
    server.settimeout(1.0) # Non si blocca per sempre aspettando un client (permette i controlli temporali)
    
    print(f"[DA] Server avviato su {ip}:{porta}")
    ultimo_invio = time.time()
    
    while True:
        # Controlla se è passato il tempo per l'aggregazione dei dati
        if time.time() - ultimo_invio >= tempo_invio_secondi:
            manda_a_iotplatform(parametri, file_iotdata)
            ultimo_invio = time.time()
        
        # Prova ad accettare un nuovo client (DC)
        try:
            conn, addr = server.accept()
            gestisci_dc(conn, addr, parametri)
        except socket.timeout:
            continue # Se nessuno si connette entro 1 secondo, ricomincia il ciclo

if __name__ == "__main__":
    main()


