import app.start as start_module


class FakeGrpcServer:
    def __init__(self) -> None:
        self.started = False
        self.stopped_grace = None

    def start(self) -> None:
        self.started = True

    def stop(self, grace: int) -> None:
        self.stopped_grace = grace


def test_start_services_starts_grpc_and_uvicorn(monkeypatch) -> None:
    fake_grpc_server = FakeGrpcServer()
    calls = {}

    def fake_create_grpc_server():
        calls["create_grpc_server_called"] = True
        return fake_grpc_server

    def fake_uvicorn_run(app_path: str, host: str, port: int) -> None:
        calls["uvicorn_app_path"] = app_path
        calls["uvicorn_host"] = host
        calls["uvicorn_port"] = port

    monkeypatch.setattr(
        start_module,
        "create_grpc_server",
        fake_create_grpc_server,
    )
    monkeypatch.setattr(
        start_module.uvicorn,
        "run",
        fake_uvicorn_run,
    )

    start_module.start_services()

    assert calls["create_grpc_server_called"] is True
    assert fake_grpc_server.started is True
    assert fake_grpc_server.stopped_grace == 0

    assert calls["uvicorn_app_path"] == "app.main:app"
    assert calls["uvicorn_host"] == start_module.settings.api_host
    assert calls["uvicorn_port"] == start_module.settings.api_port


def test_start_services_stops_grpc_when_uvicorn_finishes(monkeypatch) -> None:
    fake_grpc_server = FakeGrpcServer()

    def fake_create_grpc_server():
        return fake_grpc_server

    def fake_uvicorn_run(app_path: str, host: str, port: int) -> None:
        return None

    monkeypatch.setattr(
        start_module,
        "create_grpc_server",
        fake_create_grpc_server,
    )
    monkeypatch.setattr(
        start_module.uvicorn,
        "run",
        fake_uvicorn_run,
    )

    start_module.start_services()

    assert fake_grpc_server.started is True
    assert fake_grpc_server.stopped_grace == 0