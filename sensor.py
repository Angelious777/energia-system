import requests
import random
import time

while True:

    data = {

        "id_dispositivo": "LUZ_AULA_1",
        "zona": "AULA_1",

        "potencia": random.randint(100, 700),
        "voltaje": 220,
        "corriente": round(random.uniform(1, 5), 2),

        "temperatura": random.randint(20, 40),

        "movimiento": random.choice([True, False]),

        "estado": "ON"
    }

    requests.post(
        "http://127.0.0.1:5000/consumo",
        json=data
    )

    print(data)

    time.sleep(5)