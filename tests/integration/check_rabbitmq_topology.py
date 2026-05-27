from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


BASE_URL = os.getenv("RABBITMQ_MANAGEMENT_URL", "http://localhost:15673").rstrip("/")
USERNAME = os.getenv("RABBITMQ_MANAGEMENT_USER", "agm")
PASSWORD = os.getenv("RABBITMQ_MANAGEMENT_PASSWORD", "agm_password")
VHOST = os.getenv("RABBITMQ_VHOST", "%2F")

EXPECTED_QUEUES = {
    "auth.rpc.q",
    "periodos_materias.rpc.q",
    "docentes_alumnos.rpc.q",
    "calificaciones.rpc.q",
    "asistencias.rpc.q",
    "notificaciones.events.q",
    "notificaciones.events.dlq",
}

EXPECTED_EXCHANGES = {
    "agm.rpc",
    "agm.events",
    "agm.events.dlx",
}


def _request_json(path: str) -> list[dict]:
    password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, BASE_URL, USERNAME, PASSWORD)
    opener = urllib.request.build_opener(
        urllib.request.HTTPBasicAuthHandler(password_manager)
    )
    request = urllib.request.Request(f"{BASE_URL}{path}")
    with opener.open(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _fail(message: str) -> int:
    print(f"[ERROR] {message}", file=sys.stderr)
    return 1


def main() -> int:
    try:
        queues = {item["name"] for item in _request_json(f"/api/queues/{VHOST}")}
        exchanges = {item["name"] for item in _request_json(f"/api/exchanges/{VHOST}")}
    except urllib.error.URLError as exc:
        return _fail(f"No se pudo consultar RabbitMQ Management API: {exc}")

    missing_queues = sorted(EXPECTED_QUEUES - queues)
    missing_exchanges = sorted(EXPECTED_EXCHANGES - exchanges)

    if missing_queues:
        return _fail(f"Faltan colas RabbitMQ: {', '.join(missing_queues)}")

    if missing_exchanges:
        return _fail(f"Faltan exchanges RabbitMQ: {', '.join(missing_exchanges)}")

    print("[OK] RabbitMQ queues:")
    for queue in sorted(EXPECTED_QUEUES):
        print(f"  - {queue}")

    print("[OK] RabbitMQ exchanges:")
    for exchange in sorted(EXPECTED_EXCHANGES):
        print(f"  - {exchange}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
