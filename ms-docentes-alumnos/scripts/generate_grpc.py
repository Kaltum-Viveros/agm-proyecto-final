import sys
import os
from pathlib import Path
from grpc_tools import protoc

MS_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = MS_DIR.parent

PROTO_DIR = REPO_ROOT / "proto"
PROTO_FILE = PROTO_DIR / "auth.proto"
OUTPUT_DIR = MS_DIR / "app" / "grpc" / "generated"

GRPC_FILE = OUTPUT_DIR / "auth_pb2_grpc.py"


def patch_grpc_import() -> None:
    if not GRPC_FILE.exists():
        raise FileNotFoundError(
            "No se encontro el archivo generado auth_pb2_grpc.py"
        )

    content = GRPC_FILE.read_text(encoding="utf-8")

    content = content.replace(
        "import auth_pb2 as auth__pb2",
        "from app.grpc.generated import auth_pb2 as auth__pb2",
    )

    GRPC_FILE.write_text(
        content,
        encoding="utf-8",
    )


def generate_grpc_code() -> int:
    if not PROTO_FILE.exists():
        print(
            "No se encontro proto/auth.proto",
            file=sys.stderr,
        )
        return 1

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Initialize __init__.py if not exists
    init_file = OUTPUT_DIR / "__init__.py"
    if not init_file.exists():
        init_file.write_text("")

    result = protoc.main(
        [
            "grpc_tools.protoc",
            "-I" + str(PROTO_DIR),
            "--python_out=" + str(OUTPUT_DIR),
            "--grpc_python_out=" + str(OUTPUT_DIR),
            str(PROTO_FILE),
        ]
    )

    if result != 0:
        print(
            "Error al generar codigo gRPC",
            file=sys.stderr,
        )
        return result

    patch_grpc_import()

    print("Codigo gRPC generado correctamente")
    print("Archivo generado: " + str(OUTPUT_DIR / "auth_pb2.py"))
    print("Archivo generado: " + str(OUTPUT_DIR / "auth_pb2_grpc.py"))

    return 0


if __name__ == "__main__":
    raise SystemExit(generate_grpc_code())
