import json
import time 
from datetime import datetime
import requests

with open("clave.txt") as f:
    API_KEY= f.read().strip() #strip() quita espacios y saltos de línea al principio y final de línea

AEROPUERTOS=["VLC"]
URL="http://api.aviationstack.com/v1/flights"

def descargar(iata):
    parametros={"access_key": API_KEY, "dep_iata": iata, "limit":100}

    try:
        respuesta=requests.get(URL, params=parametros, timeout=15) #coon params y requests monta la URL completa; timeout=15: salta si no responde en 15 segundos
        respuesta.raise_for_status() #si el servidor ha respondido con un error (404,500...) lanza una excepción.
        datos=respuesta.json() # pasa de json a un objeto de paython 

    except requests.exceptions.RequestException as e:
        print(f"[{iata}] error de red")
        return None
        #si salta error en el try salta a except y devuelve None
    
    if "error" in datos: 
        print (f"[{iata}] error de la API: {datos['error']}")
        return None
    if not datos.get("data"):
        print(f"[{iata}] la API responde, pero sin vuelos")
    return datos
'''
        la API puede devolver un JSON  pero con un 
        error dentro por clave inválida o por exceder 
        los créditos de uso pero la respuesta para HTTP es 
        correcta. Comprobamos los datos manualmente y si 
        va bien devuelve los datos.
'''
    

if __name__=="__main__" : #solo se ejecuta si cuando lanzas el fichero manualmente
    sello = datetime.now().strftime("%Y%m%d_%H%M")
    for iata in AEROPUERTOS:
        datos = descargar(iata)
        if datos:
            ruta = f"datos/raw/vuelos_{iata}_{sello}.json"
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)
                '''
json.dump: de obj Python a JSON; 
----BLOQUE DE IA----: 
ensure_ascii=False: para mantener las tildes y no pasarlas a números; 
indent=2: lo deja con sangrías para poder leerlo
''' 
            print(f"[{iata}] {len(datos['data'])} vuelos -> {ruta}")
        time.sleep(1)

            


