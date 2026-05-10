from infrastructure.database.redis.redis_config import redis_client


STREAM_NAME = "consumo_stream"


def publicar_evento(data):

    redis_client.xadd(
        STREAM_NAME,
        data
    )