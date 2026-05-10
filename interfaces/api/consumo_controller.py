from flask import Blueprint
from flask import request

import uuid
from datetime import datetime

from infrastructure.database.redis.redis_config import redis_client
from infrastructure.services.event_stream_service import publicar_evento
from config.logging_config import logger

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

    try:

        evento = {

            "event_id":
                str(uuid.uuid4()),

            "dispositivo_id":
                data["dispositivo_id"],

            "timestamp": data.get(
                "timestamp",
                datetime.utcnow().isoformat()
            ),

            "consumo":
                data["consumo"],

            "zona":
                data["zona"]
        }

        logger.info(f"Nuevo evento recibido /consumo: {evento}")
        publicar_evento(evento)

        return {

            "mensaje":
                "Evento enviado correctamente",

            "event_id":
                evento["event_id"]

        }, 201

    except Exception as e:

        return {

            "error":
                str(e)

        }, 400