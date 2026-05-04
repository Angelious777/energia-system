from flask import Flask, request
from domain.services.stream_service import publicar_evento
from infrastructure.database.cassandra.cassandra_consumo_repository import CassandraConsumoRepository
from domain.services.estadistica_service import obtener_estadisticas_alertas, top_dispositivos_alertas, estadisticas_zona
from application.use_cases.verificar_health import verificar_health
from application.use_cases.obtener_recomendaciones import obtener_recomendaciones
from application.use_cases.obtener_alertas_historicas import obtener_alertas_historicas
from application.use_cases.obtener_dashboard import obtener_resumen_dashboard
from domain.services.cache_service import obtener_consumo_zona
from infrastructure.database.redis.redis_config import redis_client
from datetime import datetime
import uuid

# Importar blueprints de los controllers
from interfaces.api.consumo_controller import consumo_bp
from interfaces.api.alerta_controller import alerta_bp
from interfaces.api.dashboard_controller import dashboard_bp
from interfaces.api.health_controller import health_bp

app = Flask(__name__)

# Registrar blueprints
app.register_blueprint(consumo_bp)
app.register_blueprint(alerta_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(health_bp)


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


@app.route('/historial/<dispositivo_id>/<fecha>')
def historial(dispositivo_id, fecha):
    repository = CassandraConsumoRepository()
    consumos = repository.obtener_historial(dispositivo_id, fecha)
    datos = []
    for consumo in consumos:
        datos.append({
            "dispositivo_id": consumo.dispositivo_id,
            "fecha": consumo.timestamp.date().isoformat(),
            "timestamp": str(consumo.timestamp),
            "consumo": consumo.consumo,
            "zona": consumo.zona
        })
    return {
        "total": len(datos),
        "datos": datos
    }


@app.route('/estadisticas/alertas/<fecha>')
def estadisticas_alertas(fecha):

    resultado = obtener_estadisticas_alertas(fecha)

    return resultado


@app.route('/estadisticas/top-dispositivos/<fecha>')
def top_dispositivos(fecha):

    resultado = top_dispositivos_alertas(fecha)

    return {
        "total": len(resultado),
        "dispositivos": resultado
    }


@app.route('/estadisticas/zona/<zona>/<fecha>')
def obtener_estadisticas_zona(zona, fecha):

    resultado = estadisticas_zona(
        zona,
        fecha
    )

    return resultado


@app.route('/recomendaciones/<fecha>')
def recomendaciones(fecha):

    resultado = obtener_recomendaciones(fecha)

    return {
        "total": len(resultado),
        "recomendaciones": resultado
    }




if __name__ == '__main__':
    app.run(debug=True)