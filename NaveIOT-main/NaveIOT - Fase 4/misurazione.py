import random

def on_temperatura(N):
    TEMP = round(random.uniform(10,40), N)
    return TEMP

def on_umidita(N):
    UMID = round(random.uniform(20,90), N)
    return UMID