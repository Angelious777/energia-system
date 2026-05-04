import requests
import random
import time
from datetime import datetime

URL = "http://127.0.0.1:5000/consumo"
INTERVALO = 5  # segundos

# =========================================
# SENSORES (VARIOS DISPOSITIVOS)
# =========================================
sensores = [
    {"dispositivo_id": "LPZ_LUZ_AULA_1", "zona": "CENTRO"},
    {"dispositivo_id": "LPZ_LUZ_LAB_1", "zona": "MIRAFLORES"},
    {"dispositivo_id": "LPZ_AIRE_HOSPITAL", "zona": "MIRAFLORES"},
    {"dispositivo_id": "LPZ_ESCALERA_MECANICA", "zona": "EL_ALTO"},
    {"dispositivo_id": "LPZ_LUZ_OFICINA", "zona": "CENTRO"},
    {"dispositivo_id": "LPZ_ASCENSOR_EDIFICIO", "zona": "ZONA_SUR"},
]

print("Sensores IoT múltiples iniciados...")

# =========================================
# FUNCIÓN PARA GENERAR CONSUMO REALISTA
# =========================================
def generar_consumo():
    potencia = random.randint(100, 800)         # Watts
    voltaje = 220                               # Voltios
    corriente = round(random.uniform(0.5, 5), 2)
    temperatura = random.randint(18, 40)
    movimiento = random.choice([True, False])

    # Consumo base (P = V * I)
    consumo = voltaje * corriente

    # Ajustes dinámicos
    if movimiento:
        consumo *= 1.2

    if temperatura > 30:
        consumo *= 1.1

    # Simulación de anomalía (10%)
    if random.random() < 0.1:
        consumo *= random.uniform(2, 3)

    return round(consumo, 2)

# =========================================
# LOOP PRINCIPAL
# =========================================
while True:

    sensor = random.choice(sensores)

    consumo = generar_consumo()

    payload = {
        "dispositivo_id": sensor["dispositivo_id"],
        "zona": sensor["zona"],
        "consumo": consumo,
        "timestamp": datetime.utcnow().isoformat()
    }

    try:
        response = requests.post(URL, json=payload)
        print(f"Enviado: {payload} | Status: {response.status_code}")
    except Exception as e:
        print("Error:", e)

    time.sleep(INTERVALO)