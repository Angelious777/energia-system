from infrastructure.database.redis.redis_config import redis_client

class RedisPubSub:
    def __init__(self):
        self.pubsub = redis_client.pubsub()

    def subscribe(self, channel):
        self.pubsub.subscribe(channel)

    def publish(self, channel, message):
        redis_client.publish(channel, message)

    def listen(self):
        for message in self.pubsub.listen():
            yield message