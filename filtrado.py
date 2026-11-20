
from datetime import datetime


def filtrar_vuelos(vuelos, fecha=None):
    vuelos_filtrados = []
    vuelos_vistos = set()

    for vuelo in vuelos:
        if not isinstance(vuelo, dict):
            continue

        if not vuelo.get("dep_iata") or not vuelo.get("arr_iata"):
            continue

        if not vuelo.get("flight_iata"):
            continue

        fecha_salida = vuelo.get("dep_time")

        try:
            datetime.strptime(fecha_salida, "%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            continue

        if fecha is not None and fecha_salida.split(" ")[0] != fecha:
            continue

        clave = (
            vuelo.get("dep_iata"),
            vuelo.get("arr_iata"),
            vuelo.get("flight_iata"),
            fecha_salida
        )

        if clave in vuelos_vistos:
            continue

        vuelos_vistos.add(clave)
        vuelos_filtrados.append(vuelo)

    return vuelos_filtrados


def buscar_vuelos_directos(vuelos, origen, destino):
    vuelos_directos = []

    for vuelo in vuelos:
        if vuelo.get("dep_iata") == origen and vuelo.get("arr_iata") == destino:
            vuelos_directos.append(vuelo)

    return vuelos_directos


def buscar_conexiones(vuelos, origen, destino):
    conexiones = []

    vuelos_origen = [
        vuelo for vuelo in vuelos
        if vuelo.get("dep_iata") == origen
    ]

    vuelos_destino = [
        vuelo for vuelo in vuelos
        if vuelo.get("arr_iata") == destino
    ]

    for vuelo1 in vuelos_origen:
        for vuelo2 in vuelos_destino:
            if vuelo1.get("arr_iata") != vuelo2.get("dep_iata"):
                continue

            if vuelo1.get("flight_iata") == vuelo2.get("flight_iata"):
                continue

            try:
                llegada = datetime.strptime(
                    vuelo1.get("arr_time"),
                    "%Y-%m-%d %H:%M"
                )

                salida = datetime.strptime(
                    vuelo2.get("dep_time"),
                    "%Y-%m-%d %H:%M"
                )
            except (ValueError, TypeError):
                continue

            tiempo_escala = (salida - llegada).total_seconds() / 60

            if tiempo_escala <= 0 or tiempo_escala > 480:
                continue

            riesgo = calcular_riesgo_conexion(vuelo1, vuelo2)

            conexiones.append({
                "vuelo1": vuelo1,
                "vuelo2": vuelo2,
                "aeropuerto_escala": vuelo1.get("arr_iata"),
                "tiempo_escala_minutos": tiempo_escala,
                "riesgo": riesgo
            })

    return conexiones


def calcular_riesgo_conexion(vuelo1, vuelo2):
    try:
        llegada = datetime.strptime(
            vuelo1.get("arr_time"),
            "%Y-%m-%d %H:%M"
        )

        salida = datetime.strptime(
            vuelo2.get("dep_time"),
            "%Y-%m-%d %H:%M"
        )

        retraso = float(vuelo1.get("arr_delayed") or 0)

    except (ValueError, TypeError):
        return "No calculable"

    tiempo_disponible = (salida - llegada).total_seconds() / 60
    tiempo_disponible -= max(0, retraso)

    if tiempo_disponible < 60:
        return "Alto"
    elif tiempo_disponible < 120:
        return "Medio"
    else:
        return "Bajo"
