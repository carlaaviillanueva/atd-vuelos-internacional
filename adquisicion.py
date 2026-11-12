import requests
import json

URL = 'https://airlabs.co/api/v9/schedules'

with open('clave.txt', 'r') as archivo:
    API_KEY = archivo.read().strip()

def obtener_vuelos(AEROPUERTO):
    parametros = {
        'api_key': API_KEY,
        'dep_iata': AEROPUERTO
    }

    respuesta = requests.get(URL, params=parametros)
    respuesta.raise_for_status()
    datos = respuesta.json()

    vuelos = datos['response']

    return vuelos


