from flask import Flask, request
from services.stream_service import publicar_evento
from services.cassandra_service import obtener_historial
from services.estadistica_service import obtener_estadisticas_alertas
from config.redis_config import redis_client
from datetime import datetime
import uuid

app = Flask(__name__)

@app.route('/consumo', methods=['POST'])
def registrar_consumo():

    data = request.json

    evento = {
        "event_id": str(uuid.uuid4()),
        "dispositivo_id": data["dispositivo_id"],
        "zona": data["zona"],
        "consumo": str(data["consumo"]),
        "timestamp": datetime.now().isoformat()
    }

    publicar_evento(evento)

    return {
        "mensaje": "Evento enviado al stream",
        "evento": evento
    }


@app.route('/ultimo-consumo/<dispositivo_id>')
def obtener_ultimo_consumo(dispositivo_id):

    clave = f"consumo:dispositivo:{dispositivo_id}"

    consumo = redis_client.get(clave)

    if consumo is None:

        return {
            "mensaje": "No hay datos"
        }, 404

    return {
        "dispositivo_id": dispositivo_id,
        "ultimo_consumo": consumo
    }


@app.route('/alertas')
def obtener_alertas():

    alertas = redis_client.xrevrange(
        "alertas_stream",
        count=20
    )

    resultado = []

    for alerta_id, datos in alertas:

        resultado.append({
            "id": alerta_id,
            "datos": datos
        })

    return {
        "total": len(resultado),
        "alertas": resultado
    }


@app.route('/historial/<dispositivo_id>/<fecha>')
def historial(dispositivo_id, fecha):

    datos = obtener_historial(
        dispositivo_id,
        fecha
    )

    return {
        "total": len(datos),
        "datos": datos
    }


@app.route('/estadisticas/alertas/<fecha>')
def estadisticas_alertas(fecha):

    resultado = obtener_estadisticas_alertas(fecha)

    return resultado


if __name__ == '__main__':
    app.run(debug=True)