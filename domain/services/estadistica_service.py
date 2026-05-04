from infrastructure.database.cassandra.cassandra_alerta_repository import CassandraAlertaRepository

def obtener_estadisticas_alertas(fecha):
    repository = CassandraAlertaRepository()
    alertas = repository.obtener_por_fecha(fecha)

    resultado = {
        "MEDIA": 0,
        "ALTA": 0,
        "CRITICA": 0
    }

    for alerta in alertas:
        resultado[alerta.severidad] += 1

    return resultado


def top_dispositivos_alertas(fecha):
    repository = CassandraAlertaRepository()
    alertas = repository.obtener_por_fecha(fecha)

    conteo = {}

    for alerta in alertas:
        dispositivo = alerta.dispositivo_id
        if dispositivo not in conteo:
            conteo[dispositivo] = 0
        conteo[dispositivo] += 1

    resultado = []
    for dispositivo, cantidad in conteo.items():
        resultado.append({
            "dispositivo_id": dispositivo,
            "alertas": cantidad
        })

    resultado.sort(key=lambda x: x["alertas"], reverse=True)

    return resultado


def distribucion_zonas(fecha):
    repository = CassandraAlertaRepository()
    alertas = repository.obtener_por_fecha(fecha)

    zonas = {}
    for alerta in alertas:
        zonas.setdefault(alerta.zona, 0)
        zonas[alerta.zona] += alerta.consumo

    labels = []
    values = []
    for zona, consumo in sorted(zonas.items(), key=lambda item: item[1], reverse=True):
        labels.append(zona)
        values.append(round(consumo, 2))

    return {
        "labels": labels,
        "values": values,
        "summary": {
            "zonas_activas": len(labels),
            "consumo_total": round(sum(values), 2)
        }
    }


def tendencia_consumo(fecha, max_points=12):
    repository = CassandraAlertaRepository()
    alertas = repository.obtener_por_fecha(fecha)

    trend = {}
    for alerta in alertas:
        key = alerta.timestamp.strftime('%H:%M')
        trend[key] = trend.get(key, 0) + alerta.consumo

    labels = sorted(trend.keys())[-max_points:]
    values = [round(trend[label], 2) for label in labels]

    return {
        "labels": labels,
        "values": values
    }


def estadisticas_zona(zona, fecha):
    repository = CassandraAlertaRepository()
    alertas = repository.obtener_por_fecha(fecha)

    consumos = []
    for alerta in alertas:
        if alerta.zona == zona:
            consumos.append(alerta.consumo)

    if len(consumos) == 0:
        return {
            "mensaje": "No hay alertas en esta zona"
        }

    resultado = {
        "zona": zona,
        "total_alertas": len(consumos),
        "consumo_promedio": round(sum(consumos) / len(consumos), 2),
        "consumo_maximo": max(consumos),
        "consumo_minimo": min(consumos)
    }

    return resultado


