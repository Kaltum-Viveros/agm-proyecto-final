import aio_pika
from shared.agm_messaging.config import config

class RabbitMQConnection:
    _connection = None

    @classmethod
    async def get_connection(cls) -> aio_pika.RobustConnection:
        if cls._connection is None or cls._connection.is_closed:
            cls._connection = await aio_pika.connect_robust(config.URL)
        return cls._connection

    @classmethod
    async def close(cls):
        if cls._connection and not cls._connection.is_closed:
            await cls._connection.close()
