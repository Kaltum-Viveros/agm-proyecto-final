from app.main import app


def test_oferta_academica_routes_are_registered():
    paths = {route.path for route in app.routes}

    assert "/api/v1/materias-planes-estudio" in paths
    assert "/api/v1/materias-planes-estudio/{materia_plan_estudio_id}" in paths

    assert "/api/v1/materias-ofertadas" in paths
    assert "/api/v1/materias-ofertadas/{materia_ofertada_id}" in paths

    assert "/api/v1/materia-horarios" in paths
    assert "/api/v1/materia-horarios/{materia_horario_id}" in paths