from flask import Blueprint
from flask import request

import uuid
import datetime

from infrastructure.database.redis.redis_config import redis_client

from application.dto.consumo_dto import ConsumoDTO


consumo_bp = Blueprint(
    'consumo',
    __name__
)

STREAM_NAME = "consumo_stream"


@consumo_bp.route(
    '/consumo',
    methods=['POST']
)
def registrar_consumo():

    data = request.json

    dto = ConsumoDTO(

        dispositivo_id=data[
            "dispositivo_id"
        ],

        zona=data[
            "zona"
        ],

        consumo=data[
            "consumo"
        ]
    )

    evento = {

        "event_id": str(
            uuid.uuid4()
        ),

        "dispositivo_id":
            dto.dispositivo_id,

        "zona":
            dto.zona,

        "consumo":
            str(dto.consumo),

        "timestamp": str(
            datetime.datetime.now()
        )
    }

    redis_client.xadd(
        STREAM_NAME,
        evento
    )

    return {

        "mensaje":
            "Evento enviado al stream",

        "evento":
            evento
    }