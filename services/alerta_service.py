import uuid
from datetime import datetime
import os
from dotenv import load_dotenv
from config.cassandra_config import session

load_dotenv()

def generar_alerta(evento):

    consumo = float(evento["consumo"])

    severidad = None
    recomendacion = None
    
    UMBRAL_MEDIA = float(
        os.getenv("UMBRAL_MEDIA")
    )

    UMBRAL_ALTA = float(
        os.getenv("UMBRAL_ALTA")
    )

    UMBRAL_CRITICA = float(
        os.getenv("UMBRAL_CRITICA")
    )

    if consumo > UMBRAL_CRITICA:

        severidad = "CRITICA"

        recomendacion = (
            "Apagar dispositivo inmediatamente"
        )

    elif consumo > UMBRAL_ALTA:

        severidad = "ALTA"

        recomendacion = (
            "Reducir consumo del dispositivo"
        )

    elif consumo > UMBRAL_MEDIA:

        severidad = "MEDIA"

        recomendacion = (
            "Monitorear comportamiento"
        )

    else:

        return None

    alerta = {
        "alerta_id": uuid.uuid4(),
        "fecha": datetime.now().date(),
        "timestamp": datetime.now(),
        "dispositivo_id": evento["dispositivo_id"],
        "zona": evento["zona"],
        "consumo": consumo,
        "severidad": severidad,
        "recomendacion": recomendacion
    }

    return alerta


def obtener_alertas_historicas(fecha):

    query = """
    SELECT *
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
            "alerta_id": str(row.alerta_id),
            "dispositivo_id": row.dispositivo_id,
            "zona": row.zona,
            "consumo": row.consumo,
            "severidad": row.severidad,
            "recomendacion": row.recomendacion,
            "timestamp": str(row.timestamp)
        })

    return resultado