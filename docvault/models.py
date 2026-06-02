"""Request body schemas."""

from __future__ import annotations

from pydantic import BaseModel


class RevisionBody(BaseModel):
    size_bytes: int
