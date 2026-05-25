import asyncio
import os
import logging
from shared.agm_messaging.rpc_server import RabbitRpcServer
from shared.agm_messaging.contracts import (
    SERVICE_AUTH,
    QUEUE_AUTH_RPC,
    RPC_AUTH_VALIDATE_TOKEN,
    RPC_AUTH_GET_USER_BY_ID,
    RPC_AUTH_CHECK_ROLE,
    RPC_AUTH_CREATE_OR_GET_USER_IDENTITY,
    COMMUNICATION_MODE_GRPC
)

from app.messaging.auth_rpc_handlers import (
    validate_token_handler,
    get_user_by_id_handler,
    check_role_handler,
    create_or_get_user_identity_handler
)

logger = logging.getLogger(__name__)

async def start_rabbit_worker():
    communication_mode = os.getenv("COMMUNICATION_MODE", "grpc").lower()
    if communication_mode == COMMUNICATION_MODE_GRPC:
        logger.info("COMMUNICATION_MODE=grpc. RabbitMQ worker desactivado.")
        return

    logger.info("Iniciando RabbitMQ worker...")
    server = RabbitRpcServer(queue_name=QUEUE_AUTH_RPC)
    
    server.register_handler(RPC_AUTH_VALIDATE_TOKEN, validate_token_handler)
    server.register_handler(RPC_AUTH_GET_USER_BY_ID, get_user_by_id_handler)
    server.register_handler(RPC_AUTH_CHECK_ROLE, check_role_handler)
    server.register_handler(RPC_AUTH_CREATE_OR_GET_USER_IDENTITY, create_or_get_user_identity_handler)

    while True:
        try:
            await server.start()
        except Exception as e:
            logger.error(f"Error en RabbitMQ worker: {e}. Reintentando en 5s...")
            await asyncio.sleep(5)
