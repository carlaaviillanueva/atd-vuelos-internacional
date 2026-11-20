
from datetime import datetime, timezone


def filtrar_vuelos(vuelos, fecha=None):
    if not isinstance(vuelos, list):
        return []

    if fecha is not None:
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except (ValueError, TypeError):
            raise ValueError("La fecha debe tener el formato YYYY-MM-DD")

    vuelos_filtrados = []
    vuelos_vistos = set()

    for vuelo in vuelos:
        if not isinstance(vuelo, dict):
            continue

        origen = vuelo.get("dep_iata")
        destino = vuelo.get("arr_iata")
        codigo = vuelo.get("flight_iata")
        fecha_salida = vuelo.get("dep_time")

        if not origen or not destino or not codigo:
            continue

        if not isinstance(fecha_salida, str):
            continue

        try:
            datetime.strptime(fecha_salida, "%Y-%m-%d %H:%M")
        except ValueError:
            continue

        if fecha is not None and fecha_salida[:10] != fecha:
            continue

        clave = (origen, destino, codigo, fecha_salida)

        if clave in vuelos_vistos:
            continue

        vuelos_vistos.add(clave)
        vuelos_filtrados.append(vuelo)

    return vuelos_filtrados


def buscar_vuelos_directos(vuelos, origen, destino):
    origen = origen.strip().upper()
    destino = destino.strip().upper()

    if origen == destino:
        return []

    vuelos_directos = []

    for vuelo in vuelos:
        if not isinstance(vuelo, dict):
            continue

        if (str(vuelo.get("dep_iata", "")).upper() == origen
                and str(vuelo.get("arr_iata", "")).upper() == destino):
            vuelos_directos.append(vuelo)

    return sorted(
        vuelos_directos,
        key=lambda vuelo: str(vuelo.get("dep_time_utc") or vuelo.get("dep_time") or "")
    )


def buscar_conexiones(vuelos, origen, destino):
    origen = origen.strip().upper()
    destino = destino.strip().upper()

    if origen == destino:
        return []

    vuelos_por_salida = {}

    for vuelo in vuelos:
        if not isinstance(vuelo, dict):
            continue

        aeropuerto_salida = vuelo.get("dep_iata")

        if aeropuerto_salida:
            vuelos_por_salida.setdefault(aeropuerto_salida.upper(), []).append(vuelo)

    conexiones = []
    conexiones_vistas = set()

    for primer_vuelo in vuelos_por_salida.get(origen, []):
        escala = primer_vuelo.get("arr_iata")

        if not escala or escala.upper() in (origen, destino):
            continue

        for segundo_vuelo in vuelos_por_salida.get(escala.upper(), []):
            if str(segundo_vuelo.get("arr_iata", "")).upper() != destino:
                continue

            if primer_vuelo.get("flight_iata") == segundo_vuelo.get("flight_iata"):
                continue

            llegada_ts = primer_vuelo.get("arr_time_ts")
            salida_ts = segundo_vuelo.get("dep_time_ts")

            try:
                if llegada_ts is not None and salida_ts is not None:
                    llegada_ts = float(llegada_ts)
                    salida_ts = float(salida_ts)
                else:
                    llegada_utc = primer_vuelo.get("arr_time_utc")
                    salida_utc = segundo_vuelo.get("dep_time_utc")

                    if not llegada_utc or not salida_utc:
                        continue

                    llegada_ts = datetime.strptime(
                        llegada_utc, "%Y-%m-%d %H:%M"
                    ).replace(tzinfo=timezone.utc).timestamp()

                    salida_ts = datetime.strptime(
                        salida_utc, "%Y-%m-%d %H:%M"
                    ).replace(tzinfo=timezone.utc).timestamp()

            except (ValueError, TypeError, OverflowError):
                continue

            tiempo_escala = (salida_ts - llegada_ts) / 60

            if tiempo_escala < 30 or tiempo_escala > 480:
                continue

            clave = (
                primer_vuelo.get("flight_iata"),
                segundo_vuelo.get("flight_iata"),
                primer_vuelo.get("dep_time"),
                segundo_vuelo.get("dep_time")
            )

            if clave in conexiones_vistas:
                continue

            conexiones_vistas.add(clave)

            conexiones.append({
                "vuelo1": primer_vuelo,
                "vuelo2": segundo_vuelo,
                "aeropuerto_escala": escala.upper(),
                "tiempo_escala_minutos": round(tiempo_escala),
                "riesgo": calcular_riesgo_conexion(primer_vuelo, segundo_vuelo)
            })

    return sorted(
        conexiones,
        key=lambda conexion: conexion["tiempo_escala_minutos"]
    )


def calcular_riesgo_conexion(vuelo1, vuelo2):
    llegada_ts = vuelo1.get("arr_time_ts")
    salida_ts = vuelo2.get("dep_time_ts")

    try:
        if llegada_ts is not None and salida_ts is not None:
            llegada_ts = float(llegada_ts)
            salida_ts = float(salida_ts)
        else:
            llegada_utc = vuelo1.get("arr_time_utc")
            salida_utc = vuelo2.get("dep_time_utc")

            if not llegada_utc or not salida_utc:
                return "No calculable"

            llegada_ts = datetime.strptime(
                llegada_utc, "%Y-%m-%d %H:%M"
            ).replace(tzinfo=timezone.utc).timestamp()

            salida_ts = datetime.strptime(
                salida_utc, "%Y-%m-%d %H:%M"
            ).replace(tzinfo=timezone.utc).timestamp()

    except (ValueError, TypeError, OverflowError):
        return "No calculable"

    tiempo_escala = (salida_ts - llegada_ts) / 60

    retraso = vuelo1.get("arr_delayed")

    if retraso is None:
        llegada_estimada_ts = vuelo1.get("arr_estimated_ts")
        llegada_programada_ts = vuelo1.get("arr_time_ts")

        if llegada_estimada_ts is not None and llegada_programada_ts is not None:
            try:
                retraso = (
                    float(llegada_estimada_ts) -
                    float(llegada_programada_ts)
                ) / 60
            except (ValueError, TypeError):
                retraso = 0
        else:
            llegada_estimada_utc = vuelo1.get("arr_estimated_utc")
            llegada_programada_utc = vuelo1.get("arr_time_utc")

            if llegada_estimada_utc and llegada_programada_utc:
                try:
                    estimada = datetime.strptime(
                        llegada_estimada_utc, "%Y-%m-%d %H:%M"
                    ).replace(tzinfo=timezone.utc).timestamp()

                    programada = datetime.strptime(
                        llegada_programada_utc, "%Y-%m-%d %H:%M"
                    ).replace(tzinfo=timezone.utc).timestamp()

                    retraso = (estimada - programada) / 60

                except (ValueError, TypeError):
                    retraso = 0
            else:
                retraso = 0

    try:
        retraso = max(0, float(retraso))
    except (ValueError, TypeError):
        retraso = 0

    tiempo_disponible = tiempo_escala - retraso

    if tiempo_disponible < 60:
        return "Alto"

    if tiempo_disponible < 120:
        return "Medio"

    return "Bajo"
