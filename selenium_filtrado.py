import glob
import json
from filtrado import filtrar_vuelos

# Busca automáticamente el último archivo de VLC guardado en datos/raw
archivos = glob.glob("datos/raw/vuelos_VLC_*.json")
ruta = max(archivos)
print("Leyendo archivo:", ruta)

with open(ruta, "r", encoding="utf-8") as f:
    vuelos = json.load(f)

resultado = filtrar_vuelos(vuelos)

print("Vuelos originales:", len(vuelos))
print("Vuelos tras filtrar:", len(resultado))
for vuelo in resultado[:5]:
    print(vuelo["flight_iata"], vuelo["dep_iata"], "->", vuelo["arr_iata"], "|", vuelo["dep_time"])