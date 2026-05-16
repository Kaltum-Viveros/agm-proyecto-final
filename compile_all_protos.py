import sys
import os
from pathlib import Path
from grpc_tools import protoc

REPO_ROOT = Path(os.getcwd())
PROTO_DIR = REPO_ROOT / "proto"

# All microservices that use gRPC
targets = [
    REPO_ROOT / "ms-auth" / "app" / "grpc" / "generated",
    REPO_ROOT / "ms-periodos-materias" / "app" / "grpc" / "generated",
    REPO_ROOT / "ms-docentes-alumnos" / "app" / "grpc" / "generated",
    REPO_ROOT / "ms-calificaciones" / "app" / "grpc" / "generated",
    REPO_ROOT / "ms-asistencias" / "app" / "grpc" / "generated",
    REPO_ROOT / "ms-notificaciones" / "app" / "grpc" / "generated",
    REPO_ROOT / "ms-reportes" / "app" / "grpc" / "generated",
]

proto_files = list(PROTO_DIR.glob("*.proto"))

def patch_grpc_imports(output_dir):
    for grpc_file in output_dir.glob("*_pb2_grpc.py"):
        content = grpc_file.read_text(encoding="utf-8")
        proto_name = grpc_file.name.replace("_pb2_grpc.py", "")
        # The generated import is like `import auth_pb2 as auth__pb2`
        old_import = f"import {proto_name}_pb2 as {proto_name}__pb2"
        new_import = f"from app.grpc.generated import {proto_name}_pb2 as {proto_name}__pb2"
        
        if old_import in content:
            content = content.replace(old_import, new_import)
            grpc_file.write_text(content, encoding="utf-8")

for target_dir in targets:
    if not (target_dir.parent.parent.parent).exists():
        continue # Skip if MS folder doesn't exist
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Touch __init__.py
    (target_dir / "__init__.py").touch()
    
    for proto_file in proto_files:
        result = protoc.main([
            "grpc_tools.protoc",
            "-I" + str(PROTO_DIR),
            "--python_out=" + str(target_dir),
            "--grpc_python_out=" + str(target_dir),
            str(proto_file)
        ])
        if result != 0:
            print(f"Failed to compile {proto_file.name} for {target_dir}")
            
    patch_grpc_imports(target_dir)
    print(f"Compiled all protos for {target_dir.parent.parent.parent.name}")
