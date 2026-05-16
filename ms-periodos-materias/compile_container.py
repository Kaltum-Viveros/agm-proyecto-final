import sys
import os
from pathlib import Path
from grpc_tools import protoc

# Running inside the container at /app
APP_ROOT = Path("/app")
PROTO_DIR = APP_ROOT / "proto_files" # We'll mount or copy protos here
TARGET_DIR = APP_ROOT / "app" / "grpc" / "generated"

def patch_grpc_imports(output_dir):
    for grpc_file in output_dir.glob("*_pb2_grpc.py"):
        content = grpc_file.read_text(encoding="utf-8")
        proto_name = grpc_file.name.replace("_pb2_grpc.py", "")
        old_import = f"import {proto_name}_pb2 as {proto_name}__pb2"
        new_import = f"from app.grpc.generated import {proto_name}_pb2 as {proto_name}__pb2"
        
        if old_import in content:
            content = content.replace(old_import, new_import)
            grpc_file.write_text(content, encoding="utf-8")

if __name__ == "__main__":
    if not PROTO_DIR.exists():
        print(f"Error: {PROTO_DIR} not found")
        sys.exit(1)
        
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    (TARGET_DIR / "__init__.py").touch()
    
    proto_files = list(PROTO_DIR.glob("*.proto"))
    for proto_file in proto_files:
        result = protoc.main([
            "grpc_tools.protoc",
            "-I" + str(PROTO_DIR),
            "--python_out=" + str(TARGET_DIR),
            "--grpc_python_out=" + str(TARGET_DIR),
            str(proto_file)
        ])
        if result == 0:
            print(f"Successfully compiled {proto_file.name}")
        else:
            print(f"Failed to compile {proto_file.name}")
            
    patch_grpc_imports(TARGET_DIR)
    print("Done patching imports")
