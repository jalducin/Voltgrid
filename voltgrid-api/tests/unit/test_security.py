"""Pruebas unitarias de seguridad (sin BD)."""
from __future__ import annotations

import uuid

import pytest
from jose import JWTError

from app.core.security import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)


def test_password_hashing_roundtrip():
    h = hash_password("secret123")
    assert h != "secret123"
    assert verify_password("secret123", h)
    assert not verify_password("incorrecta", h)


def test_access_token_claims():
    uid, oid = uuid.uuid4(), uuid.uuid4()
    token = create_access_token(user_id=uid, org_id=oid, role="operator")
    payload = decode_token(token, expected_type=ACCESS_TOKEN_TYPE)
    assert payload["sub"] == str(uid)
    assert payload["org_id"] == str(oid)
    assert payload["role"] == "operator"


def test_token_type_mismatch_raises():
    uid, oid = uuid.uuid4(), uuid.uuid4()
    refresh, _ = create_refresh_token(user_id=uid, org_id=oid)
    # Decodificar un refresh como access debe fallar.
    with pytest.raises(JWTError):
        decode_token(refresh, expected_type=ACCESS_TOKEN_TYPE)
    # Como refresh, válido.
    assert decode_token(refresh, expected_type=REFRESH_TOKEN_TYPE)["type"] == REFRESH_TOKEN_TYPE


def test_hash_token_is_deterministic():
    assert hash_token("abc") == hash_token("abc")
    assert hash_token("abc") != hash_token("abd")
