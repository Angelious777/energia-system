import os
from dotenv import load_dotenv
from cassandra.cluster import Cluster

load_dotenv()

cluster = Cluster([
    os.getenv("CASSANDRA_HOST")
])

session = cluster.connect(
    os.getenv("CASSANDRA_KEYSPACE")
)