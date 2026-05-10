from infrastructure.database.redis.redis_config import redis_client
from config.logging_config import logger


STREAM_NAME = "consumo_stream"


def publicar_evento(data):
    redis_data = {
        key: str(value)
        for key, value in data.items()
    }

    logger.info(f"Publicando evento en stream {STREAM_NAME}: {redis_data}")

    redis_client.xadd(
        STREAM_NAME,
        redis_data
    )