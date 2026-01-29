import json
import time
import random
import os

from Misurazione import on_temperatura, on_umidita


# Carica il file di configurazione JSON
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


# Salva il dato rilevato da GIOT
def salva_dato(dato):
    try:
        base_dir = os.path.dirname(__file__)
        cartella_iot = os.path.join(base_dir, "IOT")
        os.makedirs(cartella_iot, exist_ok=True)

        percorso_file = os.path.join(cartella_iot, "IOTdata.dbt")

        with open(percorso_file, "a") as f:
            f.write(json.dumps(dato, indent=4))
            f.write("\n\n")

    except Exception as errore:
        print("Errore durante il salvataggio:", errore)



def main():
    base_dir = os.path.dirname(__file__)
    percorso = os.path.join(base_dir, "Parametri.conf")

    config = carica_configurazione(percorso)


    intervallo = config["TEMPO_RILEVAZIONE"]
    precisione = config["N_DECIMALI"]
    cabine_tot = config["CABINA"]
    ponti_tot = config["PONTE"]

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

            istante = time.time()

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

    # Dati finali
    print("\n-- FINE PROGRAMMA --")
    print("Numero rilevazioni:", conteggio)

    if conteggio > 0:
        print("Temperatura media:", round(tot_temp / conteggio, precisione))
        print("Umidita media:", round(tot_umid / conteggio, precisione))


if __name__ == "__main__":
    main()
