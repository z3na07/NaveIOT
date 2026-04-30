# iotgwda.py - DA / Gateway IoT - Fase 5
# Ruolo: Gateway IoT che:
#   1. Riceve dati dal DC (Raspberry Pi Pico) via Socket TCP
#   2. Cripta i dati e li pubblica su HiveMQ  → archivia_iotp.py (IoTPlatform)
#   3. Invia i dati in chiaro su ThingsBoard  → Dashboard "Cruise-IoT Monitor"
#
import socket
import json
import paho.mqtt.client as mqtt
from cripto import criptazione

def carica_config():
    """Legge parametri.json dalla cartella configurazione."""
    with open('configurazione/parametri.json', 'r') as f:
        return json.load(f)


def crea_client_hivemq(config):
    """
    Crea e connette il client MQTT verso il broker HiveMQ pubblico.
    Usato per inviare i dati CRIPTATI alla IoTPlatform (archivia_iotp.py).
    """
    client = mqtt.Client(client_id="DA-HiveMQ-" + config["IDENTITA_GIOT"])
    client.connect(config["BROKER"], config["PORTA_BROKER"], 60)
    client.loop_start()   # loop non bloccante: mantiene la connessione in background
    print(f"[DA] Connesso a HiveMQ: {config['BROKER']}:{config['PORTA_BROKER']}")
    return client


def crea_client_thingsboard(config):
    """
    Crea e connette il client MQTT verso ThingsBoard.
    L'Access Token del device funge da username (nessuna password).
    Usato per inviare la telemetria IN CHIARO alla Dashboard.
    """
    client = mqtt.Client(client_id="DA-TB-" + config["IDENTITA_GIOT"])
    client.username_pw_set(config["TB_ACCESS_TOKEN"])  # token = username
    client.connect(config["TB_HOST"], config["TB_PORT"], 60)
    client.loop_start()
    print(f"[DA] Connesso a ThingsBoard: {config['TB_HOST']}:{config['TB_PORT']}")
    return client


def prepara_payload_thingsboard(dati_dict):
    """
    Trasforma il documento IoT nel formato atteso da ThingsBoard.
    ThingsBoard si aspetta un JSON 'piatto' con le chiavi di telemetria.
    Rinomina le chiavi per avere nomi chiari nella Dashboard.
    """
    return {
        "temperatura":   dati_dict.get("temperaturam"),
        "umidita":       dati_dict.get("umiditam"),
        "cabina":        dati_dict.get("cabina"),
        "ponte":         dati_dict.get("ponte"),
        "invionumero":   dati_dict.get("invionumero"),
        "identita":      dati_dict.get("identita"),
        "dataeora":      dati_dict.get("dataeora")
    }

def main():
    # 1. Lettura configurazione
    config = carica_config()

    # 2. Connessione ai due broker MQTT
    client_hivemq = crea_client_hivemq(config)
    topic_nave    = config["TOPIC"]            # es. "iotnavi/GIOT-001/misure"

    client_tb     = crea_client_thingsboard(config)
    topic_tb      = "v1/devices/me/telemetry"  # topic standard ThingsBoard

    # 3. Avvio Socket TCP Server (in attesa dei dati dal DC / Pico)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", config["PORTA_SERVER"]))
    server_socket.listen(5)

    print(f"[DA] Gateway IoT avviato — in ascolto sulla porta {config['PORTA_SERVER']}")
    print(f"[DA] HiveMQ: {topic_nave}")
    print(f"[DA] ThingsBoard: {topic_tb}")
    print("-" * 55)

    # 4. Loop principale di ricezione
    while True:
        print("[DA] Gateway IoT in attesa di dati")
        conn, addr = server_socket.accept()
        print(f"[DA] Gateway IoT in ricezione e invio — client: {addr}")

        data = conn.recv(1024)
        if data:
            dati_chiaro = data.decode('utf-8')
            print(f"[DA DEBUG] Ricevuto dal DC : {dati_chiaro}")

            dati_criptati = criptazione(dati_chiaro)
            print(f"[DA DEBUG] Criptato (HiveMQ): {dati_criptati}")
            client_hivemq.publish(topic_nave, dati_criptati)

            try:
                payload_dict = json.loads(dati_chiaro)
                tb_payload   = json.dumps(prepara_payload_thingsboard(payload_dict))
                client_tb.publish(topic_tb, tb_payload)
                print(f"[DA DEBUG] Inviato a ThingsBoard: {tb_payload}")
            except json.JSONDecodeError as e:
                print(f"[DA ERRORE] JSON non valido ricevuto dal DC: {e}")

        conn.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[DA] Arresto gateway.")
