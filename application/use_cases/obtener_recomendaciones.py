from infrastructure.database.cassandra.cassandra_alerta_repository import CassandraAlertaRepository

def obtener_recomendaciones(fecha):
    repository = CassandraAlertaRepository()
    alertas = repository.obtener_por_fecha(fecha)
    resultado = []
    for alerta in alertas:
        resultado.append({
            "dispositivo_id": alerta.dispositivo_id,
            "zona": alerta.zona,
            "consumo": alerta.consumo,
            "severidad": alerta.severidad,
            "recomendacion": alerta.recomendacion,
            "timestamp": str(alerta.timestamp)
        })
    return resultado