from domain.services.analisis_estadistico_service import analizar_consumo
from domain.services.alerta_domain_service import generar_alerta

def motor_inteligente(datos, repository):
    # Validación básica de entrada
    required_keys = ["dispositivo_id", "consumo"]
    if not all(key in datos for key in required_keys):
        raise ValueError("Datos incompletos para motor inteligente")

    dispositivo_id = datos["dispositivo_id"]
    consumo = datos["consumo"]

    # 1. análisis estadístico
    analisis = analizar_consumo(dispositivo_id, consumo, repository)

    # 2. si no hay anomalía, cortar
    if not analisis["anomalia"]:
        return {
            "anomalia": False,
            "alerta": None,
            "recomendacion": None,
            "analisis": analisis
        }

    # 3. generar alerta (reglas de negocio)
    alerta = generar_alerta(datos, analisis)

    return {
        "anomalia": True,
        "alerta": alerta,
        "recomendacion": alerta.recomendacion if alerta else None,
        "analisis": analisis
    }