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