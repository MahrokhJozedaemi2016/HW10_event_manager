# test_security.py
import pytest
from app.utils.security import hash_password, verify_password, validate_password


def test_hash_password():
    """Test that hashing password returns a bcrypt hashed string."""
    password = "ValidPass#1234"  # Updated to meet validation rules
    hashed = hash_password(password)
    assert hashed is not None
    assert isinstance(hashed, str)
    assert hashed.startswith('$2b$')


def test_hash_password_with_different_rounds():
    """Test hashing with different cost factors."""
    password = "ValidPass#1234"  # Updated to meet validation rules
    rounds_10 = hash_password(password, rounds=10)
    rounds_12 = hash_password(password, rounds=12)
    assert rounds_10 != rounds_12, "Hashes should differ with different cost factors"


def test_verify_password_correct():
    """Test verifying the correct password."""
    password = "ValidPass#1234"  # Updated to meet validation rules
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test verifying an incorrect password."""
    password = "ValidPass#1234"  # Updated to meet validation rules
    hashed = hash_password(password)
    wrong_password = "InvalidPass#123"
    assert verify_password(wrong_password, hashed) is False


def test_verify_password_invalid_hash():
    """Test verifying a password against an invalid hash format."""
    with pytest.raises(ValueError):
        verify_password("ValidPass#1234", "invalid_hash_format")


@pytest.mark.parametrize("password,expected_error", [
    ("", "Password must be at least 8 characters long."),
    ("short", "Password must be at least 8 characters long."),
    ("noSpecial123", "Password must contain at least one special character."),
    ("NoNumber#", "Password must contain at least one number."),
    ("nouppercase123!", "Password must contain at least one uppercase letter."),
    ("NOLOWERCASE123!", "Password must contain at least one lowercase letter.")
])
def test_validate_password_invalid_cases(password, expected_error):
    """Test password validation with invalid cases."""
    with pytest.raises(ValueError, match=expected_error):
        validate_password(password)


@pytest.mark.parametrize("password", [
    "ValidPass#1234",
    "Another@Password1",
    "Strong&Pass2024!"
])
def test_validate_password_valid_cases(password):
    """Test password validation with valid cases."""
    # Should not raise any exceptions for valid passwords
    validate_password(password)


def test_verify_password_edge_cases():
    """Test verifying passwords with edge cases."""
    password = "ValidPass#1234"  # Valid password
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("InvalidPassword123!", hashed) is False


def test_hash_password_internal_error(monkeypatch):
    """Test proper error handling when an internal bcrypt error occurs."""
    def mock_bcrypt_gensalt(rounds):
        raise RuntimeError("Simulated internal error")

    # Correctly mock the bcrypt.gensalt function
    monkeypatch.setattr("bcrypt.gensalt", mock_bcrypt_gensalt)
    
    with pytest.raises(ValueError, match="Failed to hash password"):
        hash_password("ValidPass#1234")
