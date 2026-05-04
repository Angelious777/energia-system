from flask import Flask, request, render_template, send_from_directory
from domain.services.stream_service import publicar_evento
import os
from infrastructure.database.cassandra.cassandra_consumo_repository import CassandraConsumoRepository
from domain.services.estadistica_service import (
    obtener_estadisticas_alertas,
    top_dispositivos_alertas,
    estadisticas_zona,
    distribucion_zonas,
    tendencia_consumo
)
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

# Obtener ruta del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Inicializar Flask con rutas a templates y static
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'),
    static_url_path='/static'
)

# Registrar blueprints
app.register_blueprint(consumo_bp)
app.register_blueprint(alerta_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(health_bp)

# Repositorio reutilizable (evita crear uno por request)
repository = CassandraConsumoRepository()


# =========================================
# INGESTA DE EVENTOS (IMPORTANTE)
# =========================================
@app.route('/consumo', methods=['POST'])
def registrar_consumo():
    data = request.json

    try:
        evento = {
            "event_id": str(uuid.uuid4()),
            "dispositivo_id": data["dispositivo_id"],
            "timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
            "consumo": data["consumo"],
            "zona": data["zona"]
        }

        publicar_evento(evento)

        return {
            "mensaje": "Evento enviado correctamente",
            "event_id": evento["event_id"]
        }, 201

    except Exception as e:
        return {
            "error": str(e)
        }, 400


# =========================================
# REDIS - ÚLTIMO CONSUMO
# =========================================
@app.route('/ultimo-consumo/<dispositivo_id>')
def obtener_ultimo_consumo(dispositivo_id):

    clave = f"consumo:dispositivo:{dispositivo_id}"

    consumo = redis_client.get(clave)

    if consumo is None:
        return {
            "mensaje": "No hay datos"
        }, 404

    try:
        consumo = float(consumo.decode())
    except:
        consumo = consumo.decode()

    return {
        "dispositivo_id": dispositivo_id,
        "ultimo_consumo": consumo
    }


# =========================================
# CASSANDRA - HISTORIAL
# =========================================
@app.route('/historial/<dispositivo_id>/<fecha>')
def historial(dispositivo_id, fecha):

    try:
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
    except:
        return {
            "error": "Formato de fecha inválido. Use YYYY-MM-DD"
        }, 400

    consumos = repository.obtener_historial(dispositivo_id, fecha_obj)

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


# =========================================
# ESTADÍSTICAS
# =========================================
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
def obtener_estadisticas_zona_endpoint(zona, fecha):

    resultado = estadisticas_zona(
        zona,
        fecha
    )

    return resultado


# =========================================
# SERVIR ARCHIVOS ESTÁTICOS Y INDEX
# =========================================
@app.route('/')
def dashboard():
    return render_template('index.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


# =========================================
# RECOMENDACIONES
# =========================================
@app.route('/recomendaciones/<fecha>')
def recomendaciones(fecha):

    resultado = obtener_recomendaciones(fecha)

    return {
        "total": len(resultado),
        "recomendaciones": resultado
    }


# =========================================
# HEALTH CHECK
# =========================================
@app.route('/health')
def health():
    return verificar_health()


# =========================================
# DASHBOARD (OPCIONAL)
# =========================================
@app.route('/dashboard/<fecha>')
def dashboard_by_date(fecha):
    resultado = obtener_resumen_dashboard(fecha)
    return resultado


# =========================================
# ALERTAS HISTÓRICAS (OPCIONAL)
# =========================================
@app.route('/alertas/<fecha>')
def alertas_historicas(fecha):
    resultado = obtener_alertas_historicas(fecha)
    return resultado


@app.route('/dispositivos/<fecha>')
def dispositivos_por_fecha(fecha):
    resultado = top_dispositivos_alertas(fecha)
    return resultado


@app.route('/zonas/<fecha>')
def zonas_por_fecha(fecha):
    resultado = distribucion_zonas(fecha)
    resultado['tendencia'] = tendencia_consumo(fecha)
    return resultado


# =========================================
# MAIN
# =========================================
if __name__ == '__main__':
    app.run(debug=True)