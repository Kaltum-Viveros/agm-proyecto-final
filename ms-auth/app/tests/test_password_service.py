import pytest

from app.services.password_service import PasswordService


def test_hash_password_returns_different_value() -> None:
    service = PasswordService()

    hashed_password = service.hash_password("Password123")

    assert hashed_password != "Password123"
    assert isinstance(hashed_password, str)
    assert len(hashed_password) > 0


def test_verify_password_returns_true_for_valid_password() -> None:
    service = PasswordService()

    hashed_password = service.hash_password("Password123")

    assert service.verify_password("Password123", hashed_password) is True


def test_verify_password_returns_false_for_invalid_password() -> None:
    service = PasswordService()

    hashed_password = service.hash_password("Password123")

    assert service.verify_password("WrongPassword", hashed_password) is False


def test_hash_password_raises_error_for_empty_password() -> None:
    service = PasswordService()

    with pytest.raises(ValueError):
        service.hash_password("")