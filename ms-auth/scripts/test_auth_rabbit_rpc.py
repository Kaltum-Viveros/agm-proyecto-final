import asyncio
import os
import json
import logging
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
    except Exception as e:
        print(f"Error llamando RPC: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_rpc())
