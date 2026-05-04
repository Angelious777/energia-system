from config.cassandra_config import session

def guardar_consumo(evento):

    fecha = evento["timestamp"].split("T")[0]

    query = """
    INSERT INTO consumo_por_dispositivo (
        dispositivo_id,
        fecha,
        timestamp,
        consumo,
        zona
    )
    VALUES (%s, %s, %s, %s, %s)
    """

    session.execute(query, (
        evento["dispositivo_id"],
        fecha,
        evento["timestamp"],
        float(evento["consumo"]),
        evento["zona"]
    ))


def obtener_historial(dispositivo_id, fecha):

    query = """
    SELECT *
    FROM consumo_por_dispositivo
    WHERE dispositivo_id = %s
    AND fecha = %s
    """

    rows = session.execute(
        query,
        (dispositivo_id, fecha)
    )

    resultado = []

    for row in rows:

        resultado.append({
            "dispositivo_id": row.dispositivo_id,
            "fecha": str(row.fecha),
            "timestamp": str(row.timestamp),
            "consumo": row.consumo,
            "zona": row.zona
        })

    return resultado