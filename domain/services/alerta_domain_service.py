import uuid
import datetime
import os

from domain.entities.alerta import Alerta
from domain.value_objects.severidad import Severidad


UMBRAL_MEDIA = float(
    os.getenv("UMBRAL_MEDIA")
)

UMBRAL_ALTA = float(
    os.getenv("UMBRAL_ALTA")
)

UMBRAL_CRITICA = float(
    os.getenv("UMBRAL_CRITICA")
)


def generar_alerta(datos):

    consumo = float(datos["consumo"])

    severidad = None

    recomendacion = None

    if consumo > UMBRAL_CRITICA:

        severidad = Severidad.CRITICA

        recomendacion = (
            "Apagar dispositivo inmediatamente"
        )

    elif consumo > UMBRAL_ALTA:

        severidad = Severidad.ALTA

        recomendacion = (
            "Reducir consumo urgentemente"
        )

    elif consumo > UMBRAL_MEDIA:

        severidad = Severidad.MEDIA

        recomendacion = (
            "Monitorear comportamiento"
        )

    else:

        return None

    return Alerta(
        alerta_id=uuid.uuid4(),
        dispositivo_id=datos["dispositivo_id"],
        zona=datos["zona"],
        consumo=consumo,
        severidad=severidad,
        recomendacion=recomendacion,
        timestamp=datetime.datetime.now()
    )