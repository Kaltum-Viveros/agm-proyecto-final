from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Check:
    name: str
    command: list[str]


CHECKS = [
    Check(
        "Auth RPC",
        ["docker", "compose", "exec", "-T", "ms-auth", "python", "scripts/test_auth_rabbit_rpc.py"],
    ),
    Check(
        "Periodos RPC",
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "ms-periodos-materias",
            "python",
            "scripts/test_periodos_rabbit_rpc.py",
        ],
    ),
    Check(
        "Docentes-Alumnos RPC",
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "ms-docentes-alumnos",
            "python",
            "scripts/test_docentes_rabbit_rpc.py",
        ],
    ),
    Check(
        "Calificaciones RPC",
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "ms-calificaciones",
            "python",
            "scripts/test_calificaciones_rabbit_rpc.py",
        ],
    ),
    Check(
        "Asistencias RPC",
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "ms-asistencias",
            "python",
            "scripts/test_asistencias_rabbit_rpc.py",
        ],
    ),
    Check(
        "Notificaciones eventos",
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "ms-notificaciones",
            "python",
            "scripts/test_notification_events.py",
        ],
    ),
    Check(
        "Notificaciones DLQ",
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "ms-notificaciones",
            "python",
            "scripts/test_notification_dlq.py",
        ],
    ),
]


def run_check(check: Check) -> None:
    print(f"\n=== {check.name} ===", flush=True)
    print(" ".join(check.command), flush=True)
    completed = subprocess.run(check.command)
    print(f"[exit={completed.returncode}] {check.name}", flush=True)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    print(f"[OK] {check.name}", flush=True)


def main() -> int:
    for check in CHECKS:
        run_check(check)

    print("\nResumen RabbitMQ integration checks:", flush=True)
    for check in CHECKS:
        print(f"[OK] {check.name}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
