from config.cassandra_config import session

def obtener_estadisticas_alertas(fecha):

    query = """
    SELECT severidad
    FROM alertas
    WHERE fecha = %s
    """

    rows = session.execute(
        query,
        (fecha,)
    )

    resultado = {
        "MEDIA": 0,
        "ALTA": 0,
        "CRITICA": 0
    }

    for row in rows:

        resultado[row.severidad] += 1

    return resultado


def top_dispositivos_alertas(fecha):

    query = """
    SELECT dispositivo_id
    FROM alertas
    WHERE fecha = %s
    """

    rows = session.execute(
        query,
        (fecha,)
    )

    conteo = {}

    for row in rows:

        dispositivo = row.dispositivo_id

        if dispositivo not in conteo:

            conteo[dispositivo] = 0

        conteo[dispositivo] += 1

    resultado = []

    for dispositivo, cantidad in conteo.items():

        resultado.append({
            "dispositivo_id": dispositivo,
            "alertas": cantidad
        })

    resultado.sort(
        key=lambda x: x["alertas"],
        reverse=True
    )

    return resultado



def estadisticas_zona(zona, fecha):

    query = """
    SELECT zona, consumo
    FROM alertas
    WHERE fecha = %s
    """

    rows = session.execute(
        query,
        (fecha,)
    )

    consumos = []

    for row in rows:

        if row.zona == zona:

            consumos.append(row.consumo)

    if len(consumos) == 0:

        return {
            "mensaje": "No hay alertas en esta zona"
        }

    resultado = {
        "zona": zona,
        "total_alertas": len(consumos),
        "consumo_promedio": round(
            sum(consumos) / len(consumos),
            2
        ),
        "consumo_maximo": max(consumos),
        "consumo_minimo": min(consumos)
    }

    return resultado



def obtener_resumen_dashboard(fecha):

    query = """
    SELECT dispositivo_id, zona, consumo
    FROM alertas
    WHERE fecha = %s
    """

    rows = session.execute(
        query,
        (fecha,)
    )

    dispositivos = set()

    zonas = set()

    consumo_total = 0

    total_alertas = 0

    for row in rows:

        dispositivos.add(
            row.dispositivo_id
        )

        zonas.add(
            row.zona
        )

        consumo_total += row.consumo

        total_alertas += 1

    return {
        "dispositivos_activos": len(dispositivos),
        "zonas_activas": len(zonas),
        "alertas_hoy": total_alertas,
        "consumo_total": round(consumo_total, 2)
    }