import uuid
from datetime import datetime

def generar_alerta(evento):

    consumo = float(evento["consumo"])

    severidad = None
    recomendacion = None

    if consumo > 140:

        severidad = "CRITICA"

        recomendacion = (
            "Apagar dispositivo inmediatamente"
        )

    elif consumo > 120:

        severidad = "ALTA"

        recomendacion = (
            "Reducir consumo del dispositivo"
        )

    elif consumo > 100:

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