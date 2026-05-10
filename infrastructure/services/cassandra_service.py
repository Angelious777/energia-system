from infrastructure.database.cassandra.cassandra_config import session
import datetime


def _parse_timestamp(timestamp_value):
    if isinstance(timestamp_value, datetime.datetime):
        return timestamp_value

    if isinstance(timestamp_value, str):
        try:
            return datetime.datetime.fromisoformat(timestamp_value)
        except ValueError:
            try:
                return datetime.datetime.strptime(timestamp_value, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                return datetime.datetime.strptime(timestamp_value, "%Y-%m-%d %H:%M:%S")

    raise ValueError(f"Timestamp no válido: {timestamp_value}")


def _extract_fecha(timestamp_value):
    if isinstance(timestamp_value, datetime.datetime):
        return timestamp_value.date().isoformat()
    if isinstance(timestamp_value, str):
        if "T" in timestamp_value:
            return timestamp_value.split("T")[0]
        return timestamp_value.split(" ")[0]
    raise ValueError(f"Timestamp no válido: {timestamp_value}")


def _verify_session():
    if session is None:
        raise RuntimeError(
            "Cassandra no está inicializado. Verifique CASSANDRA_HOST y CASSANDRA_KEYSPACE."
        )


def guardar_consumo(evento):
    """Guarda el consumo en la tabla consumo_por_dispositivo"""
    _verify_session()
    timestamp_dt = _parse_timestamp(evento["timestamp"])
    fecha = _extract_fecha(evento["timestamp"])

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
        raise


def guardar_consumo_zona(evento):
    """Guarda el consumo en la tabla consumo_por_zona"""
    _verify_session()
    timestamp_dt = _parse_timestamp(evento["timestamp"])
    fecha = _extract_fecha(evento["timestamp"])

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
        raise


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
    _verify_session()

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

    try:
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
    except Exception as e:
        print(f"Error guardando alerta en alertas: {e}")
        raise