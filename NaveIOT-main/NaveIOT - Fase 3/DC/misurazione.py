import json
import machine
import dht
import time
import random

def carica_configurazione(file_conf="configurazione.json"):
    try:
        with open(file_conf, "r") as f:
            return json.load(f)
    except Exception:
        # Fornisce dei valori di fallback per test su PC
        return {
            "sensore": {"nome": "SIMULATO", "tmin": 0, "tmax": 40, "umin": 20, "umax": 90},
            "cablaggio": {"segnale": 0}
        }

config = carica_configurazione("configurazione.json")
pin_segnale = config["cablaggio"]["segnale"]
tipo_sensore = config["sensore"]["nome"]

sensore_dht = None
# Inizializza il sensore se siamo su MicroPython e il pin è valido
try:
    if tipo_sensore == "DHT11":
        sensore_dht = dht.DHT11(machine.Pin(pin_segnale))
    elif tipo_sensore == "DHT22":
        sensore_dht = dht.DHT22(machine.Pin(pin_segnale))
except Exception as e:
    print("Avviso: Modulo dht non disponibile o errore pin. Uso simulazione. Dettagli:", e)

def on_temperatura(n_decimali=2):
    if sensore_dht:
        try:
            sensore_dht.measure()
            return round(sensore_dht.temperature(), n_decimali)
        except Exception:
            pass
    # Simulazione in caso di errore sensore o se usato su PC
    tmin = config["sensore"]["tmin"]
    tmax = config["sensore"]["tmax"]
    return round(random.uniform(max(18.0, tmin), min(28.0, tmax)), n_decimali)

def on_umidita(n_decimali=2):
    if sensore_dht:
        try:
            # Per evitare troppe misurazioni ravvicinate, la measure l'avrà già fatta on_temperatura
            return round(sensore_dht.humidity(), n_decimali)
        except Exception:
            pass
    umin = config["sensore"]["umin"]
    umax = config["sensore"]["umax"]
    return round(random.uniform(max(40.0, umin), min(80.0, umax)), n_decimali)
