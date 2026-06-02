def test_me(client, auth_alice):
    r = client.get("/me", headers=auth_alice)
    assert r.status_code == 200
    assert r.json()["workspace_id"] == "ws-a"


def test_list_documents_is_scoped_to_workspace(client, auth_alice):
    r = client.get("/documents", headers=auth_alice)
    assert r.status_code == 200
    ids = {d["id"] for d in r.json()["documents"]}
    assert "doc-a-1" in ids
    assert "doc-b-1" not in ids


def test_get_own_document(client, auth_alice):
    r = client.get("/documents/doc-a-1", headers=auth_alice)
    assert r.status_code == 200
    body = r.json()
    assert body["used_bytes"] == 200
    assert body["sharing"]["share_token"] == "SHTOKEN-ALPHA-7731"
    assert body["storage"]["storage_key"] == "SK-ALPHA-3391"


def test_add_revision_within_quota(client, auth_alice):
    r = client.post("/documents/doc-a-1/revisions", headers=auth_alice, json={"size_bytes": 100})
    assert r.status_code == 201
    body = r.json()
    assert body["used_bytes"] == 300
    assert body["revision_id"].startswith("rev-")


def test_delete_and_restore(client, auth_alice):
    d = client.delete("/documents/doc-a-1", headers=auth_alice)
    assert d.status_code == 200
    assert d.json()["deleted"] is True
    r = client.post("/documents/doc-a-1/restore", headers=auth_alice)
    assert r.status_code == 200
    assert r.json()["deleted"] is False
