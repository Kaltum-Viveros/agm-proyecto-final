import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.agm_messaging.contracts import (
    RPC_DOCENTES_GET_ALUMNOS_BY_MATERIA,
    RPC_DOCENTES_IS_ALUMNO_EN_MATERIA,
    RPC_DOCENTES_GET_MATERIAS_BY_ALUMNO,
    RPC_DOCENTES_GET_ALUMNO_BY_ID,
    RPC_DOCENTES_GET_DOCENTE_BY_ID,
    RPC_DOCENTES_GET_DOCENTE_BY_EMAIL,
    RPC_DOCENTES_GET_DOCENTE_BY_NOMBRE,
    RPC_DOCENTES_GET_ALUMNO_BY_EMAIL,
)
from shared.agm_messaging.rpc_client import RabbitRpcClient


UNKNOWN_UUID = "00000000-0000-0000-0000-000000000000"


async def call(client: RabbitRpcClient, routing_key: str, payload: dict) -> None:
    response = await client.call(routing_key, payload)
    print(f"\n{routing_key}")
    print(json.dumps(response, indent=2, ensure_ascii=False))


async def main() -> None:
    client = RabbitRpcClient()
    try:
        await call(
            client,
            RPC_DOCENTES_GET_ALUMNO_BY_ID,
            {"alumno_id": UNKNOWN_UUID},
        )
        await call(
            client,
            RPC_DOCENTES_GET_DOCENTE_BY_ID,
            {"docente_id": UNKNOWN_UUID},
        )
        await call(
            client,
            RPC_DOCENTES_GET_ALUMNO_BY_EMAIL,
            {"email": "alumno.inexistente@example.com"},
        )
        await call(
            client,
            RPC_DOCENTES_GET_DOCENTE_BY_EMAIL,
            {"email": "docente.inexistente@example.com"},
        )
        await call(
            client,
            RPC_DOCENTES_GET_ALUMNOS_BY_MATERIA,
            {"materia_id": UNKNOWN_UUID},
        )
        await call(
            client,
            RPC_DOCENTES_IS_ALUMNO_EN_MATERIA,
            {"alumno_id": UNKNOWN_UUID, "materia_id": UNKNOWN_UUID},
        )
        await call(
            client,
            RPC_DOCENTES_GET_MATERIAS_BY_ALUMNO,
            {"alumno_id": UNKNOWN_UUID},
        )
        await call(
            client,
            RPC_DOCENTES_GET_DOCENTE_BY_NOMBRE,
            {"nombre": "Docente Inexistente"},
        )
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
