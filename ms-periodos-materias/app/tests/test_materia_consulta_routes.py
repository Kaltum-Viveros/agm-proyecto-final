from app.main import app


def test_materia_consulta_routes_are_registered():
    routes = {route.path for route in app.routes}

    assert "/api/v1/materias" in routes
    assert "/api/v1/materias/{materia_ofertada_id}" in routes
    assert "/api/v1/materias/docente/{docente_id}" in routes
    assert "/api/v1/materias/periodo/{periodo_id}" in routes
    assert "/api/v1/materias/periodo-activo" in routes


def test_periodo_activo_route_is_registered():
    routes = {route.path for route in app.routes}

    assert "/api/v1/periodos/activo" in routes