from config.redis_config import redis_client

pubsub = redis_client.pubsub()

pubsub.subscribe("consumo_excesivo")

print("Escuchando alertas...")

for mensaje in pubsub.listen():

    if mensaje["type"] == "message":

        print("\nALERTA RECIBIDA")
        print(mensaje["data"])