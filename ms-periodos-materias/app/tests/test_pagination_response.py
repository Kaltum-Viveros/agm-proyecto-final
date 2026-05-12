from app.core.pagination import build_paginated_response, get_offset


def test_get_offset_page_1():
    assert get_offset(page=1, limit=10) == 0


def test_get_offset_page_2():
    assert get_offset(page=2, limit=10) == 10


def test_build_paginated_response_empty():
    response = build_paginated_response(
        items=[],
        total=0,
        page=1,
        limit=10,
    )

    assert response["items"] == []
    assert response["total"] == 0
    assert response["page"] == 1
    assert response["limit"] == 10
    assert response["pages"] == 0


def test_build_paginated_response_with_items():
    response = build_paginated_response(
        items=[{"id": 1}],
        total=25,
        page=1,
        limit=10,
    )

    assert response["total"] == 25
    assert response["pages"] == 3