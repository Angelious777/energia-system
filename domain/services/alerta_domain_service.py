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


def generar_alerta(datos, analisis=None):

    consumo = float(datos["consumo"])

    zona = datos.get("zona", "desconocida")

    analisis = analisis or {}

    ratio = analisis.get("ratio", 1.0)

    repeticiones = analisis.get("repeticiones", 0)

    severidad = None

    recomendacion = None

    if consumo > UMBRAL_CRITICA or ratio >= 2.2:

        severidad = Severidad.CRITICA

        recomendacion = (
            f"Zona {zona}: priorizar equipos críticos y evaluar desconexión gradual de cargas no esenciales. "
            "No apagar dispositivos críticos sin coordinación."
        )

    elif consumo > UMBRAL_ALTA or ratio >= 1.5:

        severidad = Severidad.ALTA

        recomendacion = (
            f"Zona {zona}: reducir cargas no esenciales y balancear el consumo. "
            "Verificar si la crecida es recurrente antes de tomar medidas drásticas."
        )

    elif consumo > UMBRAL_MEDIA:

        severidad = Severidad.MEDIA

        recomendacion = (
            f"Zona {zona}: vigilar el comportamiento y ajustar la demanda. "
            "Mantener operaciones esenciales y evaluar la tendencia histórica."
        )

    else:

        return None

    if repeticiones >= 2 and severidad == Severidad.MEDIA:
        severidad = Severidad.ALTA
        recomendacion = (
            f"Zona {zona}: se detectaron múltiples picos recientes. "
            "Reducir cargas no críticas y preparar un plan de mitigación de demanda."
        )

    if repeticiones == 0 and severidad == Severidad.ALTA:
        recomendacion = (
            f"Zona {zona}: hay un pico de consumo aislado. "
            "Monitorear durante los próximos minutos antes de detener equipos críticos."
        )

    return Alerta(
        alerta_id=uuid.uuid4(),
        dispositivo_id=datos["dispositivo_id"],
        zona=zona,
        consumo=consumo,
        severidad=severidad,
        recomendacion=recomendacion,
        timestamp=datetime.datetime.now()
    )