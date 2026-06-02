"""docvault - a small document workspace service.

Members belong to a workspace and work with documents owned by that workspace.
They read documents, upload revisions (which consume the document's byte quota),
and soft-delete or restore documents.

A document record carries private blocks: sharing (share_token, owner_email) and
storage (storage_key, region). That data belongs to the owning workspace and must
not be readable by a member of a different workspace.

Endpoints
  GET    /me
  GET    /documents
  GET    /documents/{doc_id}
  POST   /documents/{doc_id}/revisions       body: {size_bytes}
  GET    /documents/{doc_id}/revisions
  DELETE /documents/{doc_id}
  POST   /documents/{doc_id}/restore
"""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException

from . import store
from .auth import current_user
from .models import RevisionBody

app = FastAPI(title="docvault")


def doc_full(doc: store.Document) -> dict:
    return {
        "id": doc.id,
        "workspace_id": doc.workspace_id,
        "title": doc.title,
        "quota_bytes": doc.quota_bytes,
        "used_bytes": doc.used_bytes,
        "deleted": doc.deleted,
        "sharing": doc.sharing,
        "storage": doc.storage,
    }


def doc_public(doc: store.Document) -> dict:
    return {
        "id": doc.id,
        "workspace_id": doc.workspace_id,
        "title": doc.title,
        "deleted": doc.deleted,
    }


@app.get("/me")
def me(user: store.User = Depends(current_user)):
    return {"id": user.id, "name": user.name, "role": user.role, "workspace_id": user.workspace_id}


@app.get("/documents")
def list_documents(user: store.User = Depends(current_user)):
    out = [doc_public(d) for d in store.documents.values() if d.workspace_id == user.workspace_id and not d.deleted]
    return {"documents": out}


@app.get("/documents/{doc_id}")
def get_document(doc_id: str, user: store.User = Depends(current_user)):
    doc = store.documents.get(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="document not found")
    # BUG: there is no workspace membership check, so a member of another
    # workspace receives the full record including the private sharing and
    # storage blocks. The correct behavior rejects a cross-workspace read with
    # 403 and never returns the owning workspace's private data.
    return doc_full(doc)


@app.post("/documents/{doc_id}/revisions", status_code=201)
def add_revision(doc_id: str, body: RevisionBody, user: store.User = Depends(current_user)):
    doc = store.documents.get(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="document not found")
    if doc.workspace_id != user.workspace_id:
        raise HTTPException(status_code=403, detail="not your workspace")
    if body.size_bytes <= 0:
        raise HTTPException(status_code=400, detail="size_bytes must be positive")
    # BUG: there is no check that used_bytes + size_bytes stays within
    # quota_bytes, so an upload can push a document over its byte quota. The
    # correct behavior rejects an over-quota revision with 409 and leaves
    # used_bytes unchanged.
    doc.used_bytes += body.size_bytes
    rev = store.Revision(store.next_revision_id(), doc_id, user.id, body.size_bytes)
    store.revisions[rev.id] = rev
    return {"revision_id": rev.id, "doc_id": doc_id, "size_bytes": body.size_bytes, "used_bytes": doc.used_bytes}


@app.get("/documents/{doc_id}/revisions")
def list_revisions(doc_id: str, user: store.User = Depends(current_user)):
    doc = store.documents.get(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="document not found")
    if doc.workspace_id != user.workspace_id:
        raise HTTPException(status_code=403, detail="not your workspace")
    revs = [
        {"id": r.id, "doc_id": r.doc_id, "size_bytes": r.size_bytes}
        for r in store.revisions.values()
        if r.doc_id == doc_id
    ]
    return {"revisions": revs}


@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str, user: store.User = Depends(current_user)):
    doc = store.documents.get(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="document not found")
    if doc.workspace_id != user.workspace_id:
        raise HTTPException(status_code=403, detail="not your workspace")
    doc.deleted = True
    return {"id": doc.id, "deleted": doc.deleted}


@app.post("/documents/{doc_id}/restore")
def restore_document(doc_id: str, user: store.User = Depends(current_user)):
    doc = store.documents.get(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="document not found")
    if doc.workspace_id != user.workspace_id:
        raise HTTPException(status_code=403, detail="not your workspace")
    doc.deleted = False
    return {"id": doc.id, "deleted": doc.deleted}
