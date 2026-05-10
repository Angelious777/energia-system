from infrastructure.database.cassandra.cassandra_alerta_repository import CassandraAlertaRepository
from infrastructure.database.cassandra.cassandra_alerta_por_dispositivo_repository import CassandraAlertaPorDispositivoRepository
from datetime import date

def obtener_resumen_dashboard(fecha_str):
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

    # Combinar todas las alertas, dando prioridad a las de dispositivo
    todas_alertas = alertas_dispositivo + alertas_general

    # Eliminar duplicados por alerta_id
    alertas_unicas = {}
    for alerta in todas_alertas:
        alerta_id_str = str(alerta.alerta_id)
        if alerta_id_str not in alertas_unicas:
            alertas_unicas[alerta_id_str] = alerta

    dispositivos = set()
    zonas = set()
    consumo_total = 0
    total_alertas = 0

    for alerta in alertas_unicas.values():
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