from config.cassandra_config import session

def obtener_recomendaciones(fecha):

    query = """
    SELECT
        dispositivo_id,
        zona,
        severidad,
        recomendacion,
        consumo,
        timestamp
    FROM alertas
    WHERE fecha = %s
    """

    rows = session.execute(
        query,
        (fecha,)
    )

    resultado = []

    for row in rows:

        resultado.append({
            "dispositivo_id": row.dispositivo_id,
            "zona": row.zona,
            "consumo": row.consumo,
            "severidad": row.severidad,
            "recomendacion": row.recomendacion,
            "timestamp": str(row.timestamp)
        })

    return resultado