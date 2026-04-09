# iotgwda.py - DA / Gateway IoT
import socket
import json
import paho.mqtt.client as mqtt

# Importa le funzioni esatte dal modulo originale fornito
from cripto import criptazione

def main():
    # Lettura configurazione
    with open('configurazione/parametri.json', 'r') as f:
        config = json.load(f)

    # Configurazione client MQTT (Publisher)
    client = mqtt.Client()
    client.connect(config["BROKER"], config["PORTA_BROKER"], 60)
    topic_nave = config["TOPIC"]

    # Configurazione Socket TCP (Server per la Pico)
    # Usa 0.0.0.0 per ascoltare su tutte le interfacce di rete del PC
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", config["PORTA_SERVER"]))
    server_socket.listen(5)
    
    print(f"[DA] Gateway in esecuzione. In attesa sulla porta {config['PORTA_SERVER']}...")

    while True:
        conn, addr = server_socket.accept()
        data = conn.recv(1024)
        if data:
            dati_chiaro = data.decode('utf-8')
            
            # DEBUG: stampa il dato ricevuto in chiaro
            print(f"\n[DA DEBUG] Ricevuto dal DC: {dati_chiaro}")
            
            # Criptazione con la funzione del modulo cripto.py
            dati_criptati = criptazione(dati_chiaro)
            print(f"[DA DEBUG] Dato Criptato (invio MQTT): {dati_criptati}")
            
            # Pubblicazione su Broker MQTT
            client.publish(topic_nave, dati_criptati)
            
        conn.close()

if __name__ == "__main__":
    main()