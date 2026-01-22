import json
import time
import random
from misurazione import on_temperatura, on_umidita

#Def che carica il file json da cui prendere i parametri

def carica_configurazione(percorso):
    try:
        with open(percorso, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Errore: file di configurazione mancante")
        exit(1)
    except json.JSONDecodeError:
        print("Errore: formato JSON non corretto")
        exit(1)
    except Exception as errore:
        print("Errore generico:", errore)
        exit(1)

#Def che salva il dato rilevato da DIOT
def salva_dato(dato):
    try:
        with open("IOT/iotdata.dbt", "a") as f:
            f.write(json.dumps(dato, indent=4))
            f.write("\n\n")
    except Exception as errore:
        print("Errore durante il salvataggio:", errore)


#Ciclo principale del programma

config = carica_configurazione("parametri.conf")

intervallo = config["TIMER RILEVAZIONE"]
precisione = config["NUM_DECIMALI"]
cabine_tot = config["NUM_CABINE"]
ponti_tot = config["NUM_PONTI"]

conteggio = 0
tot_temp = 0
tot_umid = 0

print("Simulazione IoT avviata (CTRL + C per uscire)")

try:
    while True:
        conteggio += 1

        id_cabina = random.randrange(1, cabine_tot + 1)
        id_ponte = random.randrange(1, ponti_tot + 1)

        temp = on_temperatura(precisione)
        umid = on_umidita(precisione)

        istante = time.strftime("%Y-%m-%d %H:%M:%S")

        pacchetto = {
            "id": conteggio,
            "cabina": id_cabina,
            "ponte": id_ponte,
            "timestamp": istante,
            "valori": {
                "temperatura": temp,
                "umidita": umid
            }
        }

        print(json.dumps(pacchetto, indent=4))
        salva_dato(pacchetto)

        tot_temp += temp
        tot_umid += umid

        time.sleep(intervallo)

except KeyboardInterrupt:
    print("\nSimulazione interrotta dall'utente")

#Stampa dei dati finali

print("--FINE PROGRAMMA-- \n")
print("Numero rilevazioni: ", conteggio)

print("Temperatura media: ", round(tot_temp / conteggio, precisione))

print("Umidita media: ", round(tot_umid / conteggio, precisione))



