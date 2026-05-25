"""
Script de prueba standalone del cliente híbrido Auth en MS-2.
Ejecutar con: python scripts/test_auth_hybrid_client.py
"""
import asyncio
import json
import logging
import os
import sys

# Asegurar que el directorio raiz del contenedor (/app) esté en sys.path
sys.path.insert(0, "/app")

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("test_hybrid")


async def main():
    from app.messaging.clients.auth_hybrid_client import AuthHybridClient

    mode = os.getenv("COMMUNICATION_MODE", "grpc")
    print(f"\n=== Test Auth Hybrid Client (COMMUNICATION_MODE={mode}) ===\n")

    client = AuthHybridClient()

    # --- 1. validate_token con token inválido ---
    print("--- Test 1: validate_token (token inválido) ---")
    result = await client.validate_token("token.invalido.xyz")
    print(f"Resultado: {json.dumps(result, indent=2, default=str)}")

    # --- 2. get_user_by_id con UUID inválido ---
    print("\n--- Test 2: get_user_by_id (UUID inválido) ---")
    result = await client.get_user_by_id("uuid-invalido")
    print(f"Resultado: {json.dumps(result, indent=2, default=str)}")

    # --- 3. check_role con UUID inválido ---
    print("\n--- Test 3: check_role (UUID inválido) ---")
    result = await client.check_role("uuid-invalido", "ADMIN")
    print(f"Resultado: {json.dumps(result, indent=2, default=str)}")

    print("\n=== Tests completados. Revisa los logs para ver el canal usado. ===")


if __name__ == "__main__":
    asyncio.run(main())
