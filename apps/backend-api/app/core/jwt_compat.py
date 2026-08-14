from __future__ import annotations

import base64
import hashlib
import hmac
import json
from typing import Any


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _encode_with_stdlib(payload: dict[str, Any], secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    encoded_header = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    encoded_payload = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    encoded_signature = _b64url_encode(signature)
    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


def encode_hs256_jwt(payload: dict[str, Any], secret: str) -> str:
    try:
        import jwt  # type: ignore

        return jwt.encode(payload, secret, algorithm="HS256")
    except Exception:
        pass

    try:
        from jose import jwt as jose_jwt  # type: ignore

        return jose_jwt.encode(payload, secret, algorithm="HS256")
    except Exception:
        return _encode_with_stdlib(payload, secret)
