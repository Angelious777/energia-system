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