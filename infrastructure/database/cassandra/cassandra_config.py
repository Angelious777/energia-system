import os
from dotenv import load_dotenv
from cassandra.cluster import Cluster, NoHostAvailable

load_dotenv()

cluster = None
session = None

try:
    cassandra_host = os.getenv("CASSANDRA_HOST", "127.0.0.1")
    cassandra_keyspace = os.getenv("CASSANDRA_KEYSPACE")

    cluster = Cluster([
        cassandra_host
    ])
    if cassandra_keyspace:
        session = cluster.connect(
            cassandra_keyspace
        )
    else:
        print("[WARNING] CASSANDRA_KEYSPACE no está definido.")
        session = None
except NoHostAvailable as error:
    print(
        "[ERROR] No se pudo conectar a Cassandra:",
        error
    )
    session = None
except Exception as error:
    print(
        "[ERROR] Error al inicializar Cassandra:",
        error
    )
    session = None