import json

ruta = "datos/raw/vuelos_VLC_20261120_1602.json"
with open(ruta, encoding="utf-8") as f:
    vuelos = json.load(f)

print("Vuelos:", len(vuelos))
print("Campos del primer vuelo:", list(vuelos[0].keys()))

# Cuántos vuelos hay de cada estado
estados = {}
for v in vuelos:
    e = v.get("status")
    estados[e] = estados.get(e, 0) + 1
print("Estados:", estados)

# Cuántos null hay en los campos de retraso
for campo in ["delayed", "dep_delayed", "arr_delayed"]:
    nulos = sum(1 for v in vuelos if v.get(campo) is None)
    print(campo, "-> null:", nulos, "de", len(vuelos))

# Valores de retraso que no son null
print([v["arr_delayed"] for v in vuelos if v.get("arr_delayed") is not None])

from datetime import datetime

print("--- Aterrizados: programada vs real ---")
formato = "%Y-%m-%d %H:%M"
for v in vuelos:
    if v.get("status") == "landed":
        prog = v.get("arr_time")
        real = v.get("arr_actual")
        diferencia = None
        if prog and real:
            t_prog = datetime.strptime(prog, formato)
            t_real = datetime.strptime(real, formato)
            diferencia = (t_real - t_prog).total_seconds() / 60
        print(v.get("flight_iata"), prog, real,
              "| arr_delayed:", v.get("arr_delayed"),
              "| diferencia calculada (min):", diferencia)

print("--- Vuelos con código compartido (cs_flight_iata no nulo) ---")
cs = [v for v in vuelos if v.get("cs_flight_iata") is not None]
print("Vuelos con cs_flight_iata:", len(cs), "de", len(vuelos))

print("--- Grupos con misma salida y llegada ---")
grupos = {}
for v in vuelos:
    clave = (v.get("dep_time"), v.get("arr_iata"), v.get("arr_time"))
    grupos.setdefault(clave, []).append(v)

for clave, lista in grupos.items():
    if len(lista) > 1:
        print(clave, "->", len(lista), "vuelos")
        for v in lista:
            print("   ", v.get("flight_iata"),
                  "| cs:", v.get("cs_flight_iata"),
                  "| estado:", v.get("status"),
                  "| retraso:", v.get("arr_delayed"))