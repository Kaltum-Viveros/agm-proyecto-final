import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "app", "grpc", "generated"))

from app.grpc.clients.auth_client import AuthClient

def run_test():
    print("Iniciando prueba de conexión gRPC (MS-3 -> MS-1)...")
    
    # 1. Crear el cliente
    try:
        client = AuthClient()
        print(f"Cliente creado apuntando a {client.host}:{client.port}")
    except Exception as e:
        print(f"Error al crear el cliente: {e}")
        sys.exit(1)

    # 2. Probar validar_token con un token falso
    print("\nProbando validate_token con un token falso...")
    result = client.validate_token("dummy_token")
    if result is None:
        print("✅ validate_token manejó correctamente el error (devolvió None).")
    else:
        print("✅ validate_token funcionó pero devolvió algo inesperado.")

    # 3. Probar get_user_by_id con un UUID falso
    print("\nProbando get_user_by_id con un UUID falso...")
    user = client.get_user_by_id("00000000-0000-0000-0000-000000000000")
    if user is None:
        print("✅ get_user_by_id manejó correctamente el error (devolvió None).")

    # 4. Probar check_role con un UUID falso
    print("\nProbando check_role...")
    allowed = client.check_role("00000000-0000-0000-0000-000000000000", "Admin")
    if not allowed:
        print("✅ check_role manejó correctamente el error (devolvió False).")

    print("\n¡Prueba de comunicación gRPC finalizada!")

if __name__ == "__main__":
    run_test()
