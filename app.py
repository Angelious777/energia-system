from flask import Flask, request
from cassandra.cluster import Cluster
import redis

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
    
    r.set(
        "LUZ_AULA_1:potencia",
        data["potencia"]
    )

    return {
        "mensaje": "dato recibido"
    }

app.run(debug=True)