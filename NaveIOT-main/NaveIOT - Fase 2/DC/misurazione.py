"""
Modulo per la simulazione della rilevazione di temperatura e umidità
da un sensore DHT11 posizionato nelle cabine di una nave da crociera.
"""

import random # Importa la libreria per generare numeri casuali

def on_temperatura(n_decimali=2):
    """
    Simula la rilevazione della temperatura.
    Args:
        n_decimali: numero di decimali per l'arrotondamento
    Returns:
        float: temperatura simulata arrotondata
    """
    # Genera un numero decimale casuale tra 18.0 e 28.0
    temperatura = random.uniform(18.0, 28.0) 
    # Arrotonda il numero al numero di decimali richiesto e lo restituisce
    return round(temperatura, n_decimali)


def on_umidita(n_decimali=2):
    """
    Simula la rilevazione dell'umidità.
    Args:
        n_decimali: numero di decimali per l'arrotondamento
    Returns:
        float: umidità simulata arrotondata
    """
    # Genera un numero decimale casuale tra 40.0 e 80.0
    umidita = random.uniform(40.0, 80.0)
    # Arrotonda e restituisce il valore
    return round(umidita, n_decimali)
