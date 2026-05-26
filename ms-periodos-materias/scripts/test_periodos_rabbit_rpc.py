import asyncio
import json
import sys

sys.path.insert(0, "/app")

from shared.agm_messaging.contracts import (
    RPC_PERIODOS_GET_MATERIA_BY_ID,
    RPC_PERIODOS_GET_MATERIA_BY_NRC,
    RPC_PERIODOS_GET_MATERIAS_BY_DOCENTE,
    RPC_PERIODOS_GET_PERIODO_ACTIVO,
)
from shared.agm_messaging.connection import RabbitMQConnection
from shared.agm_messaging.rpc_client import RabbitRpcClient


async def call_and_print(client: RabbitRpcClient, routing_key: str, payload: dict) -> None:
    print(f"\n--- {routing_key} ---")
    response = await client.call(routing_key, payload)
    print(json.dumps(response, indent=2, ensure_ascii=False, default=str))


async def main() -> None:
    client = RabbitRpcClient()
    try:
        await call_and_print(client, RPC_PERIODOS_GET_PERIODO_ACTIVO, {})
        await call_and_print(
            client,
            RPC_PERIODOS_GET_MATERIA_BY_ID,
            {"materia_id": "00000000-0000-0000-0000-000000000000"},
        )
        await call_and_print(
            client,
            RPC_PERIODOS_GET_MATERIA_BY_NRC,
            {"nrc": "00000"},
        )
        await call_and_print(
            client,
            RPC_PERIODOS_GET_MATERIAS_BY_DOCENTE,
            {"docente_id": "00000000-0000-0000-0000-000000000000"},
        )
        print("\nRabbitMQ RPC Periodos respondio correctamente.")
    finally:
        await client.close()
        await RabbitMQConnection.close()


if __name__ == "__main__":
    asyncio.run(main())
