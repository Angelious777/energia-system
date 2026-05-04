from config.redis_config import redis_client
from config.cassandra_config import session

def verificar_health():

    estado = {
        "api": "OK"
    }

    # Verificar Redis
    try:

        redis_client.ping()

        estado["redis"] = "OK"

    except:

        estado["redis"] = "ERROR"

    # Verificar Cassandra
    try:

        session.execute("SELECT now() FROM system.local")

        estado["cassandra"] = "OK"

    except:

        estado["cassandra"] = "ERROR"

    return estado