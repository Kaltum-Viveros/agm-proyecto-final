from app.main import app


def test_crud_routes_are_registered():
    paths = {route.path for route in app.routes}

    assert "/api/v1/periodos" in paths
    assert "/api/v1/periodos/{periodo_id}" in paths

    assert "/api/v1/planes-estudio" in paths
    assert "/api/v1/planes-estudio/{plan_estudio_id}" in paths

    assert "/api/v1/materias-catalogo" in paths
    assert "/api/v1/materias-catalogo/{materia_catalogo_id}" in paths