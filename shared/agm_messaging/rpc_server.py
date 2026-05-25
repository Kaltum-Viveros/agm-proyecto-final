import asyncio
import logging
import traceback
from typing import Any, Callable, Dict, Optional, Awaitable

import aio_pika

from .connection import RabbitMQConnection
from .config import config
from .envelope import MessageEnvelope

logger = logging.getLogger(__name__)

class RabbitRpcServer:
    """
    Clase base para servidores/consumidores RPC mediante RabbitMQ.
    """
    def __init__(self, queue_name: str, exchange_name: str = config.EXCHANGE_RPC):
        self.queue_name = queue_name
        self.exchange_name = exchange_name
        self.handlers: Dict[str, Callable] = {}
        self.channel: Optional[aio_pika.Channel] = None
        self._is_running = False

    def register_handler(self, routing_key: str, handler: Callable[..., Any]):
        """Registra un handler para una routing key/type especifico."""
        self.handlers[routing_key] = handler

    async def start(self):
        """Inicia el consumo de la cola asignada."""
        connection = await RabbitMQConnection.get_connection()
        self.channel = await connection.channel()
        
        # Declarar exchange
        exchange = await self.channel.declare_exchange(
            self.exchange_name, 
            aio_pika.ExchangeType.DIRECT, 
            durable=True
        )

        # Declarar cola
        queue = await self.channel.declare_queue(self.queue_name, durable=True)

        # Bindear routing keys
        for routing_key in self.handlers.keys():
            await queue.bind(exchange, routing_key=routing_key)

        self._is_running = True
        logger.info(f"[*] Escuchando RPC en la cola {self.queue_name}")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                if not self._is_running:
                    break
                await self._process_message(message, exchange)

    async def stop(self):
        self._is_running = False
        if self.channel and not self.channel.is_closed:
            await self.channel.close()

    async def _process_message(self, message: aio_pika.abc.AbstractIncomingMessage, exchange: aio_pika.abc.AbstractExchange):
        async with message.process(requeue=False):
            try:
                # Decodificar body
                envelope = MessageEnvelope.deserialize(message.body)
                
                # Obtener el operation type (del message type o envelope type o routing_key)
                operation_type = envelope.type or message.type or message.routing_key
                
                if not operation_type or operation_type not in self.handlers:
                    error_msg = f"No handler registered for type {operation_type}"
                    logger.warning(error_msg)
                    response_payload = self._build_error_response(
                        message.correlation_id, 
                        "UNKNOWN_OPERATION", 
                        error_msg
                    )
                else:
                    handler = self.handlers[operation_type]
                    try:
                        # Ejecutar handler async o sync
                        if asyncio.iscoroutinefunction(handler):
                            result = await handler(envelope.data)
                        else:
                            # Run sync in threadpool
                            result = await asyncio.to_thread(handler, envelope.data)
                        
                        response_payload = self._build_success_response(message.correlation_id, result)
                    except Exception as e:
                        logger.error(f"Error executing handler for {operation_type}: {e}")
                        traceback.print_exc()
                        response_payload = self._build_error_response(
                            message.correlation_id, 
                            "AUTH_RPC_HANDLER_ERROR", 
                            str(e)
                        )

            except Exception as e:
                logger.error(f"Critical error processing message: {e}")
                traceback.print_exc()
                response_payload = self._build_error_response(
                    message.correlation_id, 
                    "RPC_INTERNAL_ERROR", 
                    "Error decodificando o procesando mensaje"
                )

            # Responder si hay reply_to
            if message.reply_to:
                response_envelope = MessageEnvelope(data=response_payload, correlation_id=message.correlation_id)
                await self.channel.default_exchange.publish(
                    aio_pika.Message(
                        body=response_envelope.serialize(),
                        correlation_id=message.correlation_id
                    ),
                    routing_key=message.reply_to
                )

    def _build_success_response(self, correlation_id: str, data: Any) -> Dict[str, Any]:
        return {
            "correlation_id": correlation_id,
            "success": True,
            "data": data,
            "error": None
        }

    def _build_error_response(self, correlation_id: str, code: str, message: str) -> Dict[str, Any]:
        return {
            "correlation_id": correlation_id,
            "success": False,
            "data": None,
            "error": {
                "code": code,
                "message": message
            }
        }
