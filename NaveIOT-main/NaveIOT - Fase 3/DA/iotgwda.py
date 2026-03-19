import json
import socket
import time
import os
import threading
from datetime import datetime

try:
    import cripta
except ImportError:
    print("[ATTENZIONE] Modulo 'cripta' non trovato. L'esecuzione potrebbe fallire in fase di invio.")

numero_invii = 0
dati_ricevuti = {}
lock_dati = threading.Lock()

def leggi_parametri(file_parametri):
    try:
        with open(file_parametri, "r", encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERRORE] Impossibile leggere {file_parametri}: {e}")
        return {}

def salva_dati(dati, file_archivio):
    try:
        os.makedirs(os.path.dirname(file_archivio), exist_ok=True)
        with open(file_archivio, "a", encoding='utf-8') as f:
            f.write(json.dumps(dati, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[ERRORE] Salvataggio fallito: {e}")

def manda_a_iotplatform(parametri, file_archivio):
    global numero_invii, dati_ricevuti
    
    with lock_dati:
        if not dati_ricevuti or not any(len(ril) > 0 for ril in dati_ricevuti.values()):
            return
            
        numero_invii += 1
        decimali = parametri.get("N_DECIMALI", 2)
        id_gateway = parametri.get("IDENTITA_GIOT", "GW-DEFAULT")
        
        for id_dc in list(dati_ricevuti.keys()):
            rilevazioni = dati_ricevuti[id_dc]
            if not rilevazioni:
                continue
                
            media_temp = round(sum(r["temperatura"] for r in rilevazioni) / len(rilevazioni), decimali)
            media_umid = round(sum(r["umidita"] for r in rilevazioni) / len(rilevazioni), decimali)
            prima = rilevazioni[0]
            
            dato_finale = {
                "camera": prima.get("camera", ""),
                "ponte": prima.get("ponte", ""),
                "temperaturam": media_temp,
                "umiditam": media_umid,
                "dataeora": int(time.time()),
                "invionumero": numero_invii,
                "identita": id_gateway
            }
            
            print(f"\n[DA] === INVIO {numero_invii} ALL'IOTPLATFORM ===")
            print(json.dumps(dato_finale, indent=4, ensure_ascii=False))
            
            try:
                cripta.criptazione(json.dumps(dato_finale, ensure_ascii=False))
            except Exception as e:
                print(f"[ERRORE] Criptazione fallita per il DC {id_dc}: {e}")
            
            salva_dati(dato_finale, file_archivio)
            dati_ricevuti[id_dc].clear()

def gestisci_dc(connessione, indirizzo, parametri):
    global dati_ricevuti
    print(f"[DA] Nuovo DC connesso: {indirizzo}")
    try:
        config = {
            "TEMPO_RILEVAZIONE": parametri.get("TEMPO_RILEVAZIONE", 5),
            "N_DECIMALI": parametri.get("N_DECIMALI", 2)
        }
        connessione.sendall((json.dumps(config) + "\n").encode('utf-8'))
        
        buffer = ""
        while True:
            dati = connessione.recv(4096)
            if not dati: break
            buffer += dati.decode('utf-8')
            
            while '\n' in buffer:
                messaggio, buffer = buffer.split('\n', 1)
                if not messaggio.strip(): continue
                
                try:
                    dato = json.loads(messaggio)
                    print(f"\n[DA] Ricevuto da {dato.get('identita', 'Sconosciuto')}:")
                    print(json.dumps(dato, indent=4, ensure_ascii=False))
                    
                    id_dc = dato.get("identita")
                    if not id_dc: continue
                        
                    with lock_dati:
                        if id_dc not in dati_ricevuti:
                            dati_ricevuti[id_dc] = []
                        dati_ricevuti[id_dc].append({
                            "camera": dato.get("camera", "N/A"),
                            "ponte": dato.get("ponte", "N/A"),
                            "temperatura": dato["osservazione"]["temperatura"],
                            "umidita": dato["osservazione"]["umidita"]
                        })
                except json.JSONDecodeError:
                    pass

    except Exception as e:
        print(f"[DA] Errore connessione con {indirizzo}: {e}")
    finally:
        connessione.close()
        print(f"[DA] DC disconnesso: {indirizzo}")

def main():
    cartella = os.path.dirname(os.path.abspath(__file__))
    file_parametri = os.path.join(cartella, "configurazione", "parametri.json")
    file_iotdata = os.path.join(cartella, "iotp", "db.json")
    
    os.makedirs(os.path.dirname(file_parametri), exist_ok=True)
    parametri = leggi_parametri(file_parametri)
    if not parametri:
        print(f"[ERRORE] Parametri mancanti in {file_parametri}")
        return
    
    ip = parametri.get("IP_SERVER", "0.0.0.0")
    porta = parametri.get("PORTA_SERVER", 9090)
    tempo_invio_secondi = parametri.get("TEMPO_INVIO", 1) * 60
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((ip, porta))
        server.listen(5)
        server.settimeout(1.0)
        print(f"[DA] Server Multithread avviato su {ip}:{porta}")
    except Exception as e:
        print(f"[ERRORE] Impossibile avviare il server: {e}")
        return
    
    ultimo_invio = time.time()
    
    try:
        while True:
            adesso = time.time()
            if adesso - ultimo_invio >= tempo_invio_secondi:
                manda_a_iotplatform(parametri, file_iotdata)
                ultimo_invio = adesso
                
            try:
                connessione, indirizzo = server.accept()
                thread = threading.Thread(target=gestisci_dc, args=(connessione, indirizzo, parametri))
                thread.daemon = True
                thread.start()
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        # --- RIEPILOGO FINALE DA ---
        rilevazioni_residue = sum(len(ril) for ril in dati_ricevuti.values())
        print("\n" + "="*40)
        print("CHIUSURA SERVER DA (Gateway)")
        print("="*40)
        print(f"Aggregazioni inviate a IoTPlatform: {numero_invii}")
        print(f"Rilevazioni rimaste in coda: {rilevazioni_residue}")
        print("="*40)
    finally:
        server.close()

if __name__ == "__main__":
    main()
