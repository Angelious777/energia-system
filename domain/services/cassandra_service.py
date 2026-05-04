from infrastructure.database.cassandra.cassandra_config import session
import datetime

def guardar_consumo(evento):
    """Guarda el consumo en la tabla consumo_por_dispositivo"""
    fecha = evento["timestamp"].split(" ")[0]
    
    # Convertir string a datetime
    timestamp_dt = datetime.datetime.strptime(evento["timestamp"], "%Y-%m-%d %H:%M:%S.%f")

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

    try:
        session.execute(query, (
            evento["dispositivo_id"],
            fecha,
            timestamp_dt,
            float(evento["consumo"]),
            evento["zona"]
        ))
    except Exception as e:
        print(f"Error guardando consumo en consumo_por_dispositivo: {e}")


def guardar_consumo_zona(evento):
    """Guarda el consumo en la tabla consumo_por_zona"""
    fecha = evento["timestamp"].split(" ")[0]
    
    # Convertir string a datetime
    timestamp_dt = datetime.datetime.strptime(evento["timestamp"], "%Y-%m-%d %H:%M:%S.%f")

    query = """
    INSERT INTO consumo_por_zona (
        zona,
        fecha,
        timestamp,
        consumo,
        dispositivo_id
    )
    VALUES (%s, %s, %s, %s, %s)
    """

    try:
        session.execute(query, (
            evento["zona"],
            fecha,
            timestamp_dt,
            float(evento["consumo"]),
            evento["dispositivo_id"]
        ))
    except Exception as e:
        print(f"Error guardando consumo en consumo_por_zona: {e}")


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


def guardar_alerta(alerta):

    query = """
    INSERT INTO alertas (
        fecha,
        timestamp,
        alerta_id,
        dispositivo_id,
        zona,
        consumo,
        severidad,
        recomendacion
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    session.execute(query, (
        alerta["fecha"],
        alerta["timestamp"],
        alerta["alerta_id"],
        alerta["dispositivo_id"],
        alerta["zona"],
        alerta["consumo"],
        alerta["severidad"],
        alerta["recomendacion"]
    ))