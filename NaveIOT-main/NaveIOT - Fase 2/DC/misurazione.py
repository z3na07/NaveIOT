"""
Modulo per la simulazione della rilevazione di temperatura e umidità
da un sensore DHT11 posizionato nelle cabine di una nave da crociera.
"""

import random


def on_temperatura(n_decimali=2):
    """
    Simula la rilevazione della temperatura.
    
    Args:
        n_decimali: numero di decimali per l'arrotondamento
        
    Returns:
        float: temperatura simulata arrotondata
    """
    # Simula una temperatura tra 18°C e 28°C
    temperatura = random.uniform(18.0, 28.0)
    return round(temperatura, n_decimali)


def on_umidita(n_decimali=2):
    """
    Simula la rilevazione dell'umidità.
    
    Args:
        n_decimali: numero di decimali per l'arrotondamento
        
    Returns:
        float: umidità simulata arrotondata
    """
    # Simula un'umidità tra 40% e 80%
    umidita = random.uniform(40.0, 80.0)
    return round(umidita, n_decimali)
