def filtrar_vuelos(vuelos, fecha=None):
    vuelos_filtrados = []
    vuelos_vistos = set()

    for vuelo in vuelos:
        if not isinstance(vuelo,dict):
            continue

        if not vuelo.get('dep_iata') or not vuelo.get('arr_iata'):
                    continue

        codigo = vuelo.get('flight_iata')

        if not codigo:
              continue

        clave = (codigo, vuelo.get('dep_time'))

        if clave in vuelos_vistos:
              continue

        vuelos_vistos.add(clave)

        if fecha is not None:
              fecha_vuelo = vuelo.get('dep_time')

              if not isinstance(fecha_vuelo, str):
                    continue

              if not fecha_vuelo or fecha_vuelo.split(' ')[0] != fecha:
                    continue
              
        vuelos_filtrados.append(vuelo)

    return vuelos_filtrados