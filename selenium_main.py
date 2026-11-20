import json
import os
import time
from datetime import datetime
from adquisicion_selenium import obtener_vuelos

AEROPUERTOS = ["VLC", "MAD", "BCN", "LHR", "CDG", "AMS", "FRA", "FCO"]
CARPETA = "datos/raw"

if __name__ == "__main__":
    os.makedirs(CARPETA, exist_ok=True)
    sello = datetime.now().strftime("%Y%m%d_%H%M")

    for iata in AEROPUERTOS:
        vuelos = obtener_vuelos(iata)
        if vuelos:
            ruta = f"{CARPETA}/vuelos_{iata}_{sello}.json"
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(vuelos, f, ensure_ascii=False, indent=2)
            print(f"[{iata}] {len(vuelos)} vuelos -> {ruta}")
        time.sleep(5)