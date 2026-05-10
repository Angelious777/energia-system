from infrastructure.database.cassandra.cassandra_alerta_repository import CassandraAlertaRepository
from infrastructure.database.cassandra.cassandra_alerta_por_dispositivo_repository import CassandraAlertaPorDispositivoRepository
from datetime import date

def obtener_alertas_historicas(fecha_str):
    try:
        fecha = date.fromisoformat(fecha_str)
    except ValueError:
        # Si no es una fecha válida, usar la fecha actual
        fecha = date.today()

    # Obtener alertas de ambas tablas
    repository_general = CassandraAlertaRepository()
    repository_dispositivo = CassandraAlertaPorDispositivoRepository()

    alertas_general = repository_general.obtener_por_fecha(fecha_str)
    alertas_dispositivo = repository_dispositivo.obtener_por_fecha(fecha_str)

    # Combinar todas las alertas, dando prioridad a las de dispositivo (más detalladas)
    todas_alertas = alertas_dispositivo + alertas_general

    # Eliminar duplicados por alerta_id
    alertas_unicas = {}
    for alerta in todas_alertas:
        alerta_id_str = str(alerta.alerta_id)
        if alerta_id_str not in alertas_unicas:
            alertas_unicas[alerta_id_str] = alerta

    resultado = []
    for alerta in alertas_unicas.values():
        resultado.append({
            "alerta_id": str(alerta.alerta_id),
            "dispositivo_id": alerta.dispositivo_id,
            "zona": alerta.zona,
            "consumo": alerta.consumo,
            "severidad": alerta.severidad,
            "recomendacion": alerta.recomendacion,
            "timestamp": str(alerta.timestamp)
        })
    return resultado