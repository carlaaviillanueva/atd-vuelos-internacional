import requests


URL = 'https://airlabs.co/api/v9/schedules'

with open('clave.txt', 'r') as archivo:
    API_KEY = archivo.read().strip()

def obtener_vuelos(aeropuerto):
    parametros = {
        'api_key': API_KEY,
        'dep_iata': aeropuerto
    }
    try: 
        respuesta = requests.get(URL, params=parametros)
        respuesta.raise_for_status()
        datos = respuesta.json()
    except requests.exceptions.RequestException as e:
        print(f"[{aeropuerto}] error de conexión: {type(e).__name__}")
        return None
    if 'error' in datos: 
        print(f"[{aeropuerto}] error de la API: {datos['error']})")
        return None

    vuelos = datos['response']
    if not vuelos: 
        print(f"[{aeropuerto}] la API respondió pero sin vuelos")
        return None

    return vuelos