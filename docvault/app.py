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
