import logging
import asyncio
import uuid
from typing import Any, Dict

import aio_pika

from .config import config
from .envelope import MessageEnvelope
from .exceptions import RPCTimeoutException, RPCException

logger = logging.getLogger(__name__)

class RabbitRpcClient(BaseRPCClient if 'BaseRPCClient' in globals() else object):
    """
    Cliente RPC mediante RabbitMQ.
    """
    def __init__(self, exchange_name: str = config.EXCHANGE_RPC):
        self.exchange_name = exchange_name
        self.futures: Dict[str, asyncio.Future] = {}
        self.connection: aio_pika.RobustConnection = None
        self.channel: aio_pika.Channel = None
        self.callback_queue: aio_pika.Queue = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(config.URL)
        self.channel = await self.connection.channel()
        
        # Cola callback exclusiva para este cliente
        self.callback_queue = await self.channel.declare_queue(exclusive=True)

        await self.callback_queue.consume(self._on_response, no_ack=True)

    async def _on_response(self, message: aio_pika.abc.AbstractIncomingMessage):
        if message.correlation_id is None:
            return

        future = self.futures.get(message.correlation_id)
        if future is None:
            return

        try:
            envelope = MessageEnvelope.deserialize(message.body)
            future.set_result(envelope.data)
        except Exception as e:
            future.set_exception(RPCException(f"Error parseando respuesta: {e}"))

    async def call(self, routing_key: str, data: Any, timeout: int = config.RPC_TIMEOUT) -> Dict[str, Any]:
        await self.connect()

        correlation_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self.futures[correlation_id] = future

        envelope = MessageEnvelope(data=data, correlation_id=correlation_id, type=routing_key)
        
        exchange = await self.channel.declare_exchange(
            self.exchange_name, 
            aio_pika.ExchangeType.DIRECT, 
            durable=True
        )

        message = aio_pika.Message(
            body=envelope.serialize(),
            correlation_id=correlation_id,
            reply_to=self.callback_queue.name,
            type=routing_key
        )

        await exchange.publish(message, routing_key=routing_key)

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            raise RPCTimeoutException(f"Timeout RPC tras {timeout}s esperando {routing_key}")
        finally:
            self.futures.pop(correlation_id, None)
            await self.close()

    async def close(self):
        if self.channel and not self.channel.is_closed:
            await self.channel.close()
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
        self.channel = None
        self.callback_queue = None
        self.connection = None
