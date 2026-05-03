from flask import Flask, request
from cassandra.cluster import Cluster
from datetime import datetime
import redis
import json

app = Flask(__name__)


# Conexion a Redis
r = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)
print("Conectado a Redis")


# Conexion a Cassandra
cluster = Cluster(['127.0.0.1'], port=9042)
session = cluster.connect('energia')
print("Conectado a Cassandra")


@app.route('/consumo', methods=['POST'])
def registrar_consumo():

    data = request.json

    print(data)

    if data["potencia"] > 500:

        alerta = {
            "tipo": "CONSUMO_EXCESIVO",
            "dispositivo": data["id_dispositivo"]
        }

        r.lpush(
            "alertas",
            json.dumps(alerta)
        )

    # Guardar en Redis
    r.set(
        "LUZ_AULA_1:potencia",
        data["potencia"]
    )
    
    r.lpush(
        "historial:LUZ_AULA_1",
        data["potencia"]
    )
    
    r.ltrim(
        "historial:LUZ_AULA_1",
        0,
        9
    )
    
    valores = r.lrange(
        "historial:LUZ_AULA_1",
        0,
        -1
    )
    
    if promedio > 500:

        alerta = {
            "tipo": "CONSUMO_ELEVADO",
            "promedio": promedio
        }

    valores = [float(v) for v in valores]

    promedio = sum(valores) / len(valores)

    # Guardar en Cassandra
    session.execute(
        """
        INSERT INTO consumos (

            id_dispositivo,
            fecha,
            zona,

            potencia,
            voltaje,
            corriente,

            temperatura,

            movimiento,

            estado

        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            data["id_dispositivo"],
            datetime.now(),
            data["zona"],

            data["potencia"],
            data["voltaje"],
            data["corriente"],

            data["temperatura"],

            data["movimiento"],

            data["estado"]
        )
    )

    return {
        "mensaje": "dato recibido"
    }
    

app.run(debug=True)