import asyncio
import os
import json
import logging
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from shared.agm_messaging.rpc_client import RabbitRpcClient
from shared.agm_messaging.contracts import RPC_AUTH_GET_USER_BY_ID

logging.basicConfig(level=logging.INFO)

async def test_rpc():
    print("Iniciando prueba de RPC a Auth...")
    
    # Aseguramos que corra en un env con URL (ya está en compose)
    client = RabbitRpcClient()
    
    payload = {
        "user_id": "uuid-invalido"
    }
    
    try:
        response = await client.call(RPC_AUTH_GET_USER_BY_ID, payload)
        print(f"Respuesta recibida: {json.dumps(response, indent=2)}")
        print("OK: MS-1 Auth respondio por RabbitMQ RPC.")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_rpc())
