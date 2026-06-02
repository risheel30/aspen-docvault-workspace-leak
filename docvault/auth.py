"""Bearer token auth helpers."""

from __future__ import annotations

from typing import Optional

from fastapi import Header, HTTPException

from . import store


def _token_from_header(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return authorization.strip()


def current_user(authorization: Optional[str] = Header(default=None)) -> store.User:
    token = _token_from_header(authorization)
    user = store.user_by_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="missing or invalid token")
    return user
