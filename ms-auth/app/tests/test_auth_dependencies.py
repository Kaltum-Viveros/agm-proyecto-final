from app.api.dependencies import get_bearer_token


def test_get_bearer_token_returns_token_from_valid_header() -> None:
    token = get_bearer_token("Bearer access-token")

    assert token == "access-token"


def test_get_bearer_token_accepts_lowercase_scheme() -> None:
    token = get_bearer_token("bearer access-token")

    assert token == "access-token"


def test_get_bearer_token_returns_empty_string_when_header_is_missing() -> None:
    token = get_bearer_token(None)

    assert token == ""


def test_get_bearer_token_returns_empty_string_when_scheme_is_invalid() -> None:
    token = get_bearer_token("Basic access-token")

    assert token == ""


def test_get_bearer_token_returns_empty_string_when_format_is_invalid() -> None:
    token = get_bearer_token("Bearer")

    assert token == ""