# iotp/archivia_iotp.py - Piattaforma IoT (Subscriber MQTT)
import json
import paho.mqtt.client as mqtt
import sys
import os

# Aggiunge la cartella superiore al percorso di Python per poter importare 'cripto.py'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa l'esatta funzione di decriptazione dal tuo modulo originale
from cripto import decriptazione

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        topic_sub = userdata["topic"]
        print(f"Connesso al Broker MQTT. Sottoscrizione al topic: {topic_sub}")
        client.subscribe(topic_sub)
    else:
        print(f"Errore di connessione: {rc}")

def on_message(client, userdata, msg):
    payload_criptato = msg.payload.decode('utf-8')
    
    # 1. Decriptazione usando il modulo cripto.py
    dati_chiaro = decriptazione(payload_criptato)
    
    print(f"\n[IOTP DEBUG] Messaggio dal topic: {msg.topic}")
    print(f"[IOTP DEBUG] Dati decriptati: {dati_chiaro}")
    
    # 2. Archiviazione su dbplatform.json
    nome_file_db = userdata["dbfile"]["file"]
    modo_scrittura = userdata["dbfile"]["modo"]
    
    # Imposta il percorso del database affinché venga creato dentro la cartella 'iotp'
    percorso_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), nome_file_db)
    
    with open(percorso_db, modo_scrittura) as f:
        f.write(dati_chiaro + "\n")

def main():
    # Legge il file iotp.json nella stessa cartella 'iotp'
    percorso_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iotp.json')
    with open(percorso_config, 'r') as f:
        config = json.load(f)

    # Configurazione Subscriber MQTT
    client = mqtt.Client(userdata=config)
    client.on_connect = on_connect
    client.on_message = on_message

    host_broker = config["broker"]["host"]
    porta_broker = config["broker"]["porta"]

    client.connect(host_broker, porta_broker, 60)
    
    print("[IOTP] Piattaforma IoT in ascolto...")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n[IOTP] Arresto ricevitore.")

if __name__ == "__main__":
    main()