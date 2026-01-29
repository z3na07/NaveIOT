import json
import socket
import time
import os
import signal
import sys
from datetime import datetime
import cripta

# Variabili globali
numero_invii = 0
dati_ricevuti = {}  # Qui salvo tutti i dati che arrivano dai DC

# Legge il file parametri.conf
def leggi_parametri(file_parametri):
    f = open(file_parametri, "r")
    parametri = json.load(f)
    f.close()
    return parametri

# Salva i dati nel file iotdata.dbt
def salva_dati(dati, file_archivio):
    f = open(file_archivio, "a", encoding='utf-8')
    f.write(json.dumps(dati, ensure_ascii=False) + "\n")
    f.close()

# Elabora i dati e li manda all'IoTPlatform
def manda_a_iotplatform(parametri, file_archivio):
    global numero_invii, dati_ricevuti
    
    # Se non ho dati, non faccio niente
    if len(dati_ricevuti) == 0:
        return
    
    numero_invii = numero_invii + 1
    decimali = parametri["N_DECIMALI"]
    id_gateway = parametri["IDENTITA_GIOT"]
    
    # Lista che conterrà i dati elaborati
    lista_elaborati = []
    
    # Per ogni DC calcolo le medie
    for id_dc in dati_ricevuti:
        rilevazioni = dati_ricevuti[id_dc]
        
        if len(rilevazioni) == 0:
            continue
        
        # Calcolo la media delle temperature
        somma_temp = 0
        for r in rilevazioni:
            somma_temp = somma_temp + r["temperatura"]
        media_temp = somma_temp / len(rilevazioni)
        media_temp = round(media_temp, decimali)
        
        # Calcolo la media delle umidità
        somma_umid = 0
        for r in rilevazioni:
            somma_umid = somma_umid + r["umidita"]
        media_umid = somma_umid / len(rilevazioni)
        media_umid = round(media_umid, decimali)
        
        # Prendo i dati fissi dalla prima rilevazione
        prima = rilevazioni[0]
        
        # Creo il dato elaborato
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
    
    # Creo il dato finale da mandare
    dato_finale = {
        "idgateway": id_gateway,
        "invionumero": numero_invii,
        "timestamp": datetime.now().isoformat(),
        "dati": lista_elaborati
    }
    
    # Stampo cosa sto mandando
    print(f"\n[DA] === INVIO {numero_invii} ALL'IOTPLATFORM ===")
    print(json.dumps(dato_finale, indent=4, ensure_ascii=False))
    
    # Cripto il dato (in realtà non lo cripto davvero)
    dato_json = json.dumps(dato_finale, ensure_ascii=False)
    dato_criptato = cripta.criptazione(dato_json)
    
    # Salvo il dato NON criptato
    salva_dati(dato_finale, file_archivio)
    
    print(f"[DA] Salvato! (invio #{numero_invii})")
    
    # Svuoto i dati per il prossimo giro
    dati_ricevuti.clear()

# Gestisce un client che si connette
def gestisci_dc(connessione, indirizzo, parametri):
    global dati_ricevuti
    
    print(f"[DA] Nuovo DC connesso: {indirizzo}")
    
    try:
        # Mando i parametri al DC
        config = {
            "TEMPO_RILEVAZIONE": parametri["TEMPO_RILEVAZIONE"],
            "N_DECIMALI": parametri["N_DECIMALI"]
        }
        connessione.sendall(json.dumps(config).encode('utf-8'))
        print(f"[DA] Mandati parametri a {indirizzo}")
        
        # Buffer per i dati che arrivano
        buffer = ""
        
        # Ricevo i dati dal DC
        while True:
            dati = connessione.recv(4096)
            if not dati:
                break
            
            buffer = buffer + dati.decode('utf-8')
            
            # Processo tutti i messaggi completi
            while '\n' in buffer:
                messaggio = buffer.split('\n')[0]
                buffer = buffer.split('\n', 1)[1]
                
                try:
                    dato = json.loads(messaggio)
                    
                    # Stampo cosa ho ricevuto
                    print(f"\n[DA] Ricevuto da {dato['identita']}:")
                    print(json.dumps(dato, indent=4, ensure_ascii=False))
                    
                    # Salvo il dato
                    id_dc = dato["identita"]
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
                    print(f"[DA] Errore nel messaggio da {indirizzo}")
    
    except Exception as errore:
        print(f"[DA] Errore con {indirizzo}: {errore}")
    finally:
        connessione.close()
        print(f"[DA] Chiusa connessione con {indirizzo}")

# Gestisce CTRL+C
def quando_premo_ctrlc(sig, frame):
    global numero_invii
    print(f"\n\n[DA] CTRL+C premuto!")
    print(f"[DA] Invii fatti all'IoTPlatform: {numero_invii}")
    print(f"[DA] -- FINE --")
    sys.exit(0)

# PROGRAMMA PRINCIPALE
def main():
    global numero_invii
    
    # Registro la funzione per CTRL+C
    signal.signal(signal.SIGINT, quando_premo_ctrlc)
    
    # Leggo i parametri
    cartella = os.path.dirname(__file__)
    file_parametri = os.path.join(cartella, "parametri.conf")
    parametri = leggi_parametri(file_parametri)
    
    ip = parametri["IP_SERVER"]
    porta = parametri["PORTA_SERVER"]
    tempo_invio_minuti = parametri["TEMPO_INVIO"]
    tempo_invio_secondi = tempo_invio_minuti * 60
    
    # Percorso del file dove salvare i dati
    file_iotdata = os.path.join(os.path.dirname(cartella), "IOTP", "iotdata.dbt")
    
    # Creo il socket del server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((ip, porta))
    server.listen(5)
    server.settimeout(1.0)  # Timeout di 1 secondo
    
    print(f"[DA] Server avviato su {ip}:{porta}")
    print(f"[DA] Invio dati ogni {tempo_invio_minuti} minuti")
    print(f"[DA] In attesa di DC... (CTRL+C per fermare)")
    
    ultimo_invio = time.time()
    
    try:
        # Ciclo infinito
        while True:
            # Controllo se devo mandare i dati
            adesso = time.time()
            if adesso - ultimo_invio >= tempo_invio_secondi:
                manda_a_iotplatform(parametri, file_iotdata)
                ultimo_invio = adesso
            
            # Accetto nuove connessioni
            try:
                conn, addr = server.accept()
                gestisci_dc(conn, addr, parametri)
            except socket.timeout:
                # Timeout normale, continuo
                continue
                
    except KeyboardInterrupt:
        quando_premo_ctrlc(None, None)
    finally:
        server.close()

if __name__ == "__main__":
    main()
