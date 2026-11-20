#TODO ESTE BLOQUE ESTÁ HECHO CON IA PARA COMPROBAR QUE NUESTRO CÓDIGO LO FILTRA TODO BIEN.
#LA IA NOS IBA DICIENDO TODO LO QUE NOS FALTABA Y NOSOTROS LO IBAMOS PROGRAMANDO SEGÚN LO QUE NOS DECÍA.
import json
from filtrado import filtrar_vuelos

ruta = "datos/raw/vuelos_VLC_20261118_2338.json"

with open(ruta, "r", encoding="utf-8") as archivo:
    vuelos = json.load(archivo)

print("Vuelos originales:", len(vuelos))

resultado = filtrar_vuelos(vuelos, fecha=None)

print("Vuelos después del filtrado:", len(resultado))

for vuelo in vuelos:
    for campo in ["dep_iata", "arr_iata", "flight_iata", "dep_time"]:
        if vuelo.get(campo) is None:
            print("Vuelo con campo vacío:", vuelo.get("flight_iata"), campo)

print("\n--- Información adicional ---")

for campo in ["arr_time", "arr_actual", "arr_delayed",
              "dep_delayed", "cs_flight_iata"]:

    nulos = sum(1 for vuelo in vuelos if vuelo.get(campo) is None)

    print(campo, ":", nulos, "valores vacíos de", len(vuelos))


print("\n--- Vuelos con información de retraso ---")

for vuelo in vuelos:
    if vuelo.get("arr_delayed") is not None:
        print(
            vuelo.get("flight_iata"),
            "Salida:", vuelo.get("dep_delayed"),
            "Llegada:", vuelo.get("arr_delayed")
        )

print("\n--- Aeropuertos de llegada ---")

llegadas = set()

for vuelo in vuelos:
    llegadas.add(vuelo.get("arr_iata"))

print(llegadas)

print("\n--- Aeropuertos de salida --22-")

salidas = set()

for vuelo in vuelos:
    salidas.add(vuelo.get("dep_iata"))

print(salidas)