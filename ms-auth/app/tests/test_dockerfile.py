from pathlib import Path


MS_AUTH_DIR = Path(__file__).resolve().parents[2]
DOCKERFILE_PATH = MS_AUTH_DIR / "Dockerfile"


def test_dockerfile_exists() -> None:
    assert DOCKERFILE_PATH.exists()


def test_dockerfile_uses_python_312() -> None:
    content = DOCKERFILE_PATH.read_text(encoding="utf-8")

    assert "FROM python:3.12-slim" in content


def test_dockerfile_exposes_rest_and_grpc_ports() -> None:
    content = DOCKERFILE_PATH.read_text(encoding="utf-8")

    assert "EXPOSE 8001" in content
    assert "EXPOSE 50051" in content


def test_dockerfile_starts_rest_and_grpc_entrypoint() -> None:
    content = DOCKERFILE_PATH.read_text(encoding="utf-8")

    assert 'CMD ["python", "-m", "app.start"]' in content