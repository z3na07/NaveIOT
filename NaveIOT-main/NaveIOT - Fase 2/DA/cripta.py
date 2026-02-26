# Modulo di criptazione
# Script: cripto.py
# Algoritmo: da definire
# Simulazione con sostituzione della lettera 'a' con '*'
def criptazione(payload): # Funzione per criptare il messaggio
    # Sostituisce tutte le lettere 'a' con un asterisco '*'
    criptato = payload.replace("a","*") 
    return criptato

def decriptazione(payload): # Funzione per decriptare
    # Fa l'esatto opposto: trasforma gli '*' in 'a'
    decriptato = payload.replace("*","a")
    return decriptato
