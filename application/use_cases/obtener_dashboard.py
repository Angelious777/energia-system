from infrastructure.database.cassandra.cassandra_alerta_repository import CassandraAlertaRepository

def obtener_resumen_dashboard(fecha):
    repository = CassandraAlertaRepository()
    alertas = repository.obtener_por_fecha(fecha)

    dispositivos = set()
    zonas = set()
    consumo_total = 0
    total_alertas = 0

    for alerta in alertas:
        dispositivos.add(alerta.dispositivo_id)
        zonas.add(alerta.zona)
        consumo_total += alerta.consumo
        total_alertas += 1

    return {
        "dispositivos_activos": len(dispositivos),
        "zonas_activas": len(zonas),
        "alertas_hoy": total_alertas,
        "consumo_total": round(consumo_total, 2),
        "total_consumo": round(consumo_total, 2)
    }