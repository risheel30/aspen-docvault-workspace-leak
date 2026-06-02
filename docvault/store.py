from __future__ import annotations

from typing import Dict, Optional


class User:
    def __init__(self, user_id: str, name: str, token: str, role: str, workspace_id: str):
        self.id = user_id
        self.name = name
        self.token = token
        self.role = role
        self.workspace_id = workspace_id


class Document:
    def __init__(
        self,
        doc_id: str,
        workspace_id: str,
        title: str,
        quota_bytes: int,
        used_bytes: int,
        share_token: str,
        owner_email: str,
        storage_key: str,
        region: str,
    ):
        self.id = doc_id
        self.workspace_id = workspace_id
        self.title = title
        self.quota_bytes = quota_bytes
        self.used_bytes = used_bytes
        self.deleted = False
        self.sharing = {"share_token": share_token, "owner_email": owner_email}
        self.storage = {"storage_key": storage_key, "region": region}


class Revision:
    def __init__(self, rev_id: str, doc_id: str, user_id: str, size_bytes: int):
        self.id = rev_id
        self.doc_id = doc_id
        self.user_id = user_id
        self.size_bytes = size_bytes


users: Dict[str, User] = {}
documents: Dict[str, Document] = {}
revisions: Dict[str, Revision] = {}

_rev_counter = {"n": 0}


def next_revision_id() -> str:
    _rev_counter["n"] += 1
    return f"rev-{_rev_counter['n']:04d}"


def user_by_token(token: Optional[str]) -> Optional[User]:
    if not token:
        return None
    for u in users.values():
        if u.token == token:
            return u
    return None


def reset_store() -> None:
    users.clear()
    documents.clear()
    revisions.clear()
    _rev_counter["n"] = 0

    users["u-alice"] = User("u-alice", "Alice", "tok-alice", "member", "ws-a")
    users["u-bob"] = User("u-bob", "Bob", "tok-bob", "member", "ws-a")
    users["u-carol"] = User("u-carol", "Carol", "tok-carol", "admin", "ws-a")
    users["u-dave"] = User("u-dave", "Dave", "tok-dave", "member", "ws-b")

    documents["doc-a-1"] = Document(
        "doc-a-1", "ws-a", "Q3 Roadmap", 1000, 200,
        "SHTOKEN-ALPHA-7731", "alice@acme.test", "SK-ALPHA-3391", "us-east",
    )
    documents["doc-a-2"] = Document(
        "doc-a-2", "ws-a", "Budget Plan", 800, 100,
        "SHTOKEN-ALPHA-5520", "carol@acme.test", "SK-ALPHA-8852", "us-east",
    )
    documents["doc-b-1"] = Document(
        "doc-b-1", "ws-b", "Vendor List", 500, 50,
        "SHTOKEN-BETA-9920", "dave@globex.test", "SK-BETA-7742", "eu-west",
    )
