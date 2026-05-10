from domain.services.estadistica_zona_service import EstadisticaZonaService
from infrastructure.database.cassandra.cassandra_estadistica_zona_repository import CassandraEstadisticaZonaRepository
from datetime import date

def obtener_estadisticas_por_zona(fecha_str: str):
    try:
        fecha = date.fromisoformat(fecha_str)
    except ValueError:
        raise ValueError("Formato de fecha inválido")

    repository = CassandraEstadisticaZonaRepository()
    service = EstadisticaZonaService(repository)

    return service.obtener_estadisticas_por_fecha(fecha)

def obtener_estadistica_zona_individual(zona: str, fecha_str: str):
    try:
        fecha = date.fromisoformat(fecha_str)
    except ValueError:
        raise ValueError("Formato de fecha inválido")

    repository = CassandraEstadisticaZonaRepository()
    service = EstadisticaZonaService(repository)

    return service.obtener_estadistica_zona(zona, fecha)

def calcular_estadisticas_zona(zona: str, fecha_str: str):
    try:
        fecha = date.fromisoformat(fecha_str)
    except ValueError:
        raise ValueError("Formato de fecha inválido")

    repository = CassandraEstadisticaZonaRepository()
    service = EstadisticaZonaService(repository)

    service.calcular_y_guardar_estadistica_zona(zona, fecha)
    return {"mensaje": "Estadísticas calculadas y guardadas"}