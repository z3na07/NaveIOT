import json
import socket
import time
import os
import threading
from datetime import datetime
import cripta

numero_invii = 0
dati_ricevuti = {}

def leggi_parametri(file_parametri):
    with open(file_parametri, "r") as f:
        return json.load(f)

def salva_dati(dati, file_archivio):
    os.makedirs(os.path.dirname(file_archivio), exist_ok=True)
    with open(file_archivio, "a", encoding='utf-8') as f:
        f.write(json.dumps(dati, ensure_ascii=False) + "\n")

def manda_a_iotplatform(parametri, file_archivio):
    global numero_invii, dati_ricevuti
    
    if len(dati_ricevuti) == 0:
        return
    
    numero_invii += 1
    decimali = parametri["N_DECIMALI"]
    id_gateway = parametri["IDENTITA_GIOT"]
    
    # Crea un blocco unico per ogni DC 
    for id_dc in list(dati_ricevuti.keys()):
        rilevazioni = dati_ricevuti[id_dc]
        if len(rilevazioni) == 0:
            continue
            
        media_temp = round(sum(r["temperatura"] for r in rilevazioni) / len(rilevazioni), decimali)
        media_umid = round(sum(r["umidita"] for r in rilevazioni) / len(rilevazioni), decimali)
        prima = rilevazioni[0]
        
        # Struttura esatta richiesta da PDF: flat structure e timestamp unix
        dato_finale = {
            "camera": prima["camera"],
            "ponte": prima["ponte"],
            "temperaturam": media_temp,
            "umiditam": media_umid,
            "dataeora": int(time.time()),
            "invionumero": numero_invii,
            "identita": id_gateway
        }
        
        print(f"\n[DA] === INVIO {numero_invii} ALL'IOTPLATFORM ===")
        print(json.dumps(dato_finale, indent=4, ensure_ascii=False))
        
        # Criptazione fittizia come da specifiche
        dato_json = json.dumps(dato_finale, ensure_ascii=False)
        dato_criptato = cripta.criptazione(dato_json)
        
        # Salvataggio nel database non criptato db.json
        salva_dati(dato_finale, file_archivio)
        
        # Pulizia post-invio
        dati_ricevuti[id_dc].clear()

def gestisci_dc(connessione, indirizzo, parametri):
    global dati_ricevuti
    print(f"[DA] Nuovo DC connesso: {indirizzo}")
    try:
        # Invia la configurazione al client
        config = {
            "TEMPO_RILEVAZIONE": parametri["TEMPO_RILEVAZIONE"],
            "N_DECIMALI": parametri["N_DECIMALI"]
        }
        connessione.sendall((json.dumps(config) + "\n").encode('utf-8'))
        
        buffer = ""
        while True:
            dati = connessione.recv(4096)
            if not dati:
                break
            buffer += dati.decode('utf-8')
            
            while '\n' in buffer:
                messaggio, buffer = buffer.split('\n', 1)
                if not messaggio: continue
                dato = json.loads(messaggio)
                
                print(f"\n[DA] Ricevuto da {dato['identita']}:")
                print(json.dumps(dato, indent=4, ensure_ascii=False))
                
                id_dc = dato["identita"]
                if id_dc not in dati_ricevuti:
                    dati_ricevuti[id_dc] = []
                    
                dati_ricevuti[id_dc].append({
                    "camera": dato["camera"],
                    "ponte": dato["ponte"],
                    "temperatura": dato["osservazione"]["temperatura"],
                    "umidita": dato["osservazione"]["umidita"]
                })
    except Exception as e:
        print(f"[DA] Errore di connessione: {e}")
    finally:
        connessione.close()

def main():
    cartella = os.path.dirname(__file__)
    # Percorsi aggiornati come specificato nel PDF
    file_parametri = os.path.join(cartella, "configurazione", "parametri.json")
    file_iotdata = os.path.join(cartella, "iotp", "db.json")
    
    os.makedirs(os.path.dirname(file_parametri), exist_ok=True)
    if not os.path.exists(file_parametri):
        print(f"[ERRORE] File {file_parametri} non trovato. Crealo nella cartella 'configurazione'.")
        return

    parametri = leggi_parametri(file_parametri)
    
    ip = parametri.get("IP_SERVER", "127.0.0.1")
    porta = parametri.get("PORTA_SERVER", 9090)
    tempo_invio_secondi = parametri["TEMPO_INVIO"] * 60
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((ip, porta))
    server.listen(5)
    server.settimeout(1.0)
    
    print(f"[DA] Server Multithread avviato su {ip}:{porta}")
    
    ultimo_invio = time.time()
    
    try:
        while True:
            adesso = time.time()
            if adesso - ultimo_invio >= tempo_invio_secondi:
                manda_a_iotplatform(parametri, file_iotdata)
                ultimo_invio = adesso
                
            try:
                connessione, indirizzo = server.accept()
                # Nuovo server multithread per gestire multipli dc.py
                thread = threading.Thread(target=gestisci_dc, args=(connessione, indirizzo, parametri))
                thread.start()
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        print(f"\n[DA] Ferrmato. Totale misurazioni elaborate per IoTPlatform: {numero_invii}")
        server.close()

if __name__ == "__main__":
    main()