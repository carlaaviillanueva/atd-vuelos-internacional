from filtrado import filtrar_vuelos

vuelos = [
    {
        "flight_iata": "IB100",
        "dep_iata": "VLC",
        "arr_iata": "FCO",
        "dep_time": "2026-11-19 10:00"
    },
    {
        "flight_iata": "FR200",
        "dep_iata": "FCO",
        "arr_iata": "CDG",
        "dep_time": "2026-11-19 13:00"
    },
    {
        "flight_iata": "VY300",
        "dep_iata": "VLC",
        "arr_iata": "MAD",
        "dep_time": "2026-11-20 09:00"
    }
]

resultado = filtrar_vuelos(vuelos, fecha="2026-11-19")

print("Vuelos encontrados:", len(resultado))

for vuelo in resultado:
    print(vuelo["flight_iata"], vuelo["dep_iata"], "->", vuelo["arr_iata"])
