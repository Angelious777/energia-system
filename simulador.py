import requests
import random
import time

SEGUNDOS_INTERVALO = 5

URL = "http://127.0.0.1:5000/consumo"

dispositivos = [
    {
        "dispositivo_id": "AULA_1",
        "zona": "BLOQUE_A"
    },
    {
        "dispositivo_id": "AULA_2",
        "zona": "BLOQUE_A"
    },
    {
        "dispositivo_id": "LAB_1",
        "zona": "BLOQUE_B"
    },
    {
        "dispositivo_id": "OFICINA_1",
        "zona": "ADMIN"
    }
]

print("Simulador IoT iniciado...")

while True:

    dispositivo = random.choice(dispositivos)

    consumo = round(
        random.uniform(20, 150),
        2
    )

    payload = {
        "dispositivo_id": dispositivo["dispositivo_id"],
        "zona": dispositivo["zona"],
        "consumo": consumo
    }

    response = requests.post(
        URL,
        json=payload
    )

    print(f"Enviado: {payload}")

    time.sleep(SEGUNDOS_INTERVALO)