import asyncio
import json
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from shared.agm_messaging.contracts import (
    RPC_ASISTENCIAS_GET_ASISTENCIA_ALUMNO,
    RPC_ASISTENCIAS_GET_ASISTENCIAS_MATERIA,
    RPC_ASISTENCIAS_GET_ESTADISTICAS_ASISTENCIA,
)
from shared.agm_messaging.connection import RabbitMQConnection
from shared.agm_messaging.rpc_client import RabbitRpcClient


UUID_INEXISTENTE = "00000000-0000-0000-0000-000000000000"


async def call_and_print(client: RabbitRpcClient, routing_key: str, payload: dict) -> None:
    response = await client.call(routing_key, payload)
    print(f"\n{routing_key}")
    print(json.dumps(response, indent=2, ensure_ascii=False, default=str))


async def main() -> None:
    client = RabbitRpcClient()
    try:
        await call_and_print(
            client,
            RPC_ASISTENCIAS_GET_ASISTENCIA_ALUMNO,
            {"alumno_id": UUID_INEXISTENTE, "materia_id": UUID_INEXISTENTE},
        )
        await call_and_print(
            client,
            RPC_ASISTENCIAS_GET_ASISTENCIAS_MATERIA,
            {"materia_id": UUID_INEXISTENTE},
        )
        await call_and_print(
            client,
            RPC_ASISTENCIAS_GET_ESTADISTICAS_ASISTENCIA,
            {"materia_id": UUID_INEXISTENTE},
        )
        print("\nOK: MS-5 Asistencias respondio por RabbitMQ RPC.")
    finally:
        await client.close()
        await RabbitMQConnection.close()


if __name__ == "__main__":
    asyncio.run(main())
