# Gestione sensore temperatura e umidità
# DHT11 (celeste) o DHT22 (bianco)
# Raspberry Pico WH
# Utilizzo libreria dht
#
# Script: pico3.py
#
import time
from machine import Pin
import dht 
#
# Funzioni
#
def leggi_temp(N_PIN): 
    #
    sensor = dht.DHT11(Pin(N_PIN))      # Sensore celeste
    #sensor = dht.DHT22(Pin(N_PIN))     # Sensore bianco
    #
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        print('Temperatura: %3.1f C' %temp)
        print('Umidità: %3.1f %%' %hum)
    
    except OSError as e:
        print('Problemi con il sensore...')
    TEMP = temp
    UMI  = hum
    return TEMP,UMI
#
# Main
#
INTERVALLO = 5                 # Intervallo cattura e invio dati in secondi
PIN_SEGNALE = 0                # PIN associato al PIN del sensore DHT11 che invia i dati digitali
#
try:
    while True:
        TEMPERATURA,UMIDITA = leggi_temp(PIN_SEGNALE)  # Acquisizione dati e conversione stringa
        print ("Misura:" + str(TEMPERATURA).encode("utf-8"))
        print ("Umidità:"+ str(UMIDITA).encode("utf-8"))
        # 
        # Ritardo lettura
        time.sleep(INTERVALLO)                  # Attesa
# Uscita forzata
except KeyboardInterrupt:
        print ("Stop acquisizione")