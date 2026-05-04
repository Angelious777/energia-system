import requests
import random
import time
from datetime import datetime

URL = "http://127.0.0.1:5000/consumo"
INTERVALO = 5  # segundos entre ciclos

# =========================================
# DISPOSITIVOS (ESCENARIO LA PAZ)
# =========================================
dispositivos = [
    # CENTRO
    {"dispositivo_id": "LPZ_UMSA_AULA_1", "zona": "CENTRO", "tipo": "educacion"},
    {"dispositivo_id": "LPZ_UMSA_AULA_2", "zona": "CENTRO", "tipo": "educacion"},
    {"dispositivo_id": "LPZ_ALCALDIA", "zona": "CENTRO", "tipo": "oficina"},
    {"dispositivo_id": "LPZ_BANCO_CENTRAL", "zona": "CENTRO", "tipo": "oficina"},

    # MIRAFLORES
    {"dispositivo_id": "LPZ_HOSPITAL_OBRERO", "zona": "MIRAFLORES", "tipo": "hospital"},
    {"dispositivo_id": "LPZ_CLINICA", "zona": "MIRAFLORES", "tipo": "hospital"},

    # ZONA SUR
    {"dispositivo_id": "LPZ_MEGACENTER", "zona": "ZONA_SUR", "tipo": "comercial"},
    {"dispositivo_id": "LPZ_SUPERMERCADO", "zona": "ZONA_SUR", "tipo": "comercial"},

    # EL ALTO
    {"dispositivo_id": "LPZ_TELEFERICO_ROJO", "zona": "EL_ALTO", "tipo": "transporte"},
    {"dispositivo_id": "LPZ_TELEFERICO_AMARILLO", "zona": "EL_ALTO", "tipo": "transporte"},
    {"dispositivo_id": "LPZ_AEROPUERTO", "zona": "EL_ALTO", "tipo": "infraestructura"},
]

# =========================================
# CONSUMO BASE POR ZONA
# =========================================
def consumo_base(zona):
    if zona == "EL_ALTO":
        return random.uniform(80, 200)
    elif zona == "CENTRO":
        return random.uniform(50, 140)
    elif zona == "MIRAFLORES":
        return random.uniform(60, 150)
    elif zona == "ZONA_SUR":
        return random.uniform(40, 120)
    return random.uniform(30, 100)

# =========================================
# AJUSTE POR TIPO
# =========================================
def ajustar_tipo(consumo, tipo):
    if tipo == "hospital":
        return consumo * 1.3
    elif tipo == "comercial":
        return consumo * 1.2
    elif tipo == "transporte":
        return consumo * 1.5
    elif tipo == "infraestructura":
        return consumo * 1.4
    return consumo

# =========================================
# GENERADOR FINAL
# =========================================
def generar_consumo(dispositivo):
    consumo = consumo_base(dispositivo["zona"])
    consumo = ajustar_tipo(consumo, dispositivo["tipo"])

    # anomalía (10%)
    if random.random() < 0.1:
        consumo *= random.uniform(2, 3)

    return round(consumo, 2)

# =========================================
# SIMULACIÓN
# =========================================
print("Simulador multi-dispositivo iniciado...")

while True:

    print("\n--- NUEVO CICLO ---")

    # envía datos de TODOS los dispositivos
    for dispositivo in dispositivos:

        consumo = generar_consumo(dispositivo)

        payload = {
            "dispositivo_id": dispositivo["dispositivo_id"],
            "zona": dispositivo["zona"],
            "consumo": consumo,
            "timestamp": datetime.utcnow().isoformat()
        }

        try:
            response = requests.post(URL, json=payload)
            print(f"{dispositivo['dispositivo_id']} -> {consumo} | {response.status_code}")
        except Exception as e:
            print("Error:", e)

    time.sleep(INTERVALO)