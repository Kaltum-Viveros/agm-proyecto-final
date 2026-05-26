import asyncio
import logging

import aio_pika
from shared.agm_messaging.config import config

logger = logging.getLogger(__name__)


class RabbitMQConnection:
    _connection = None
    _loop = None

    @classmethod
    async def get_connection(cls) -> aio_pika.RobustConnection:
        current_loop = asyncio.get_running_loop()
        loop_changed = cls._loop is not None and cls._loop is not current_loop

        if loop_changed:
            await cls.reset()

        if cls._connection is None or cls._connection.is_closed:
            cls._connection = await aio_pika.connect_robust(config.URL)
            cls._loop = current_loop
        return cls._connection

    @classmethod
    async def close(cls):
        if cls._connection and not cls._connection.is_closed:
            await cls._connection.close()
        cls._connection = None
        cls._loop = None

    @classmethod
    async def reset(cls):
        try:
            if cls._connection and not cls._connection.is_closed:
                await cls._connection.close()
        except Exception as exc:
            logger.warning("Error closing RabbitMQ connection during loop reset: %s", exc)
        finally:
            cls._connection = None
            cls._loop = None
