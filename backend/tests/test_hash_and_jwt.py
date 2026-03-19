# tests/test_hash_and_jwt.py
import pytest
from app.auth.hash import hash_password, verify_password
from app.auth.jwt import create_access_token, decode_token

def test_hash_and_verify():
    pw = "StrongPassw0rd!"
    h = hash_password(pw)
    assert verify_password(pw, h) is True
    assert verify_password("wrong", h) is False

def test_jwt_create_decode():
    token = create_access_token(123, expires_seconds=60)
    payload = decode_token(token)
    assert payload["sub"] == "123"
    assert payload["type"] == "access"
