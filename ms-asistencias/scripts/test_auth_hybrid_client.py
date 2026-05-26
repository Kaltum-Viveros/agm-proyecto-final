import asyncio
import logging
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.messaging.clients.auth_hybrid_client import AuthHybridClient


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    mode = os.getenv("COMMUNICATION_MODE", "hybrid")
    client = AuthHybridClient()

    print(f"=== Test AuthHybridClient MS-5 (COMMUNICATION_MODE={mode}) ===")

    print("\n--- validate_token token invalido ---")
    validate_result = await client.validate_token("token.invalido.xyz")
    print(validate_result)

    print("\n--- get_user_by_id UUID invalido ---")
    user_result = await client.get_user_by_id("uuid-invalido")
    print(user_result)

    print("\n--- check_role UUID invalido ---")
    role_result = await client.check_role("uuid-invalido", "DOCENTE")
    print(role_result)


if __name__ == "__main__":
    asyncio.run(main())
