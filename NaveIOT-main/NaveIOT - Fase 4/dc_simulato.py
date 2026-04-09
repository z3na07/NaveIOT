# dc_simulato.py - Device Controller Virtuale per test su PC
import json
import time
import socket

# Importiamo il modulo fornito dal prof per simulare i dati
import misurazione

def leggi_configurazione():
    with open('da.json', 'r') as f:
        return json.load(f)

def main():
    config_da = leggi_configurazione()
    # Usiamo localhost (127.0.0.1) perché sia il DC che il Gateway girano sullo stesso PC
    ip_da = "127.0.0.1" 
    porta_da = config_da['porta']
    invio_numero = 1

    print(f"[DC VIRTUALE] Avvio simulazione sensore...")
    print(f"[DC VIRTUALE] Invio dati a {ip_da}:{porta_da}")

    while True:
        # Lettura dati simulati (usando la libreria misurazione.py)
        # Passiamo 2 come parametro per avere 2 cifre decimali, come richiesto dal file
        temp = misurazione.on_temperatura(2)
        umid = misurazione.on_umidita(2)
        
        # reazione payload come da PDF
        payload = {
            "cabina": 1,
            "ponte": 1,
            "temperaturam": float(temp),
            "umiditam": float(umid),
            "dataeora": int(time.time()),
            "invionumero": invio_numero,
            "identita": "GIOT-001"
        }
        
        dati_json = json.dumps(payload)
        
        # DEBUG: Stampa del dato inviato
        print(f"[DC DEBUG] Dati inviati in chiaro -> {dati_json}")
        
        # Invio via Socket locale al DA (Gateway)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip_da, porta_da))
            s.sendall(dati_json.encode('utf-8'))
            s.close()
            invio_numero += 1
        except Exception as e:
            print(f"[DC ERRORE] Gateway non trovato. Assicurati che iotgwda.py sia in esecuzione! ({e})")
            
        time.sleep(5)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n[DC VIRTUALE] Esecuzione fermata.")