from infrastructure.database.cassandra.cassandra_alerta_repository import CassandraAlertaRepository

def obtener_alertas_historicas(fecha):
    repository = CassandraAlertaRepository()
    alertas = repository.obtener_por_fecha(fecha)
    resultado = []
    for alerta in alertas:
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