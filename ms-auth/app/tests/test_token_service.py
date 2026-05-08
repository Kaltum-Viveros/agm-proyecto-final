import pytest

from app.services.token_service import TokenService


def test_generate_secure_token_returns_non_empty_string() -> None:
    service = TokenService()

    token = service.generate_secure_token()

    assert isinstance(token, str)
    assert len(token) > 0


def test_generate_secure_token_returns_different_values() -> None:
    service = TokenService()

    first_token = service.generate_secure_token()
    second_token = service.generate_secure_token()

    assert first_token != second_token


def test_hash_token_returns_sha256_hash() -> None:
    service = TokenService()

    token_hash = service.hash_token("my-token")

    assert isinstance(token_hash, str)
    assert len(token_hash) == 64
    assert token_hash != "my-token"


def test_hash_token_raises_error_for_empty_token() -> None:
    service = TokenService()

    with pytest.raises(ValueError):
        service.hash_token("")


def test_verify_token_hash_returns_true_for_valid_token() -> None:
    service = TokenService()

    token = "my-token"
    token_hash = service.hash_token(token)

    assert service.verify_token_hash(token, token_hash) is True


def test_verify_token_hash_returns_false_for_invalid_token() -> None:
    service = TokenService()

    token_hash = service.hash_token("my-token")

    assert service.verify_token_hash("wrong-token", token_hash) is False