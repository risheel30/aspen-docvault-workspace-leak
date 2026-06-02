"""Shared pytest fixtures.

Each test runs against a freshly seeded store. Auth handles are named after the
seeded users so tests read cleanly.
"""

import pytest
from fastapi.testclient import TestClient

from docvault.app import app
from docvault import store


@pytest.fixture(autouse=True)
def fresh_store():
    store.reset_store()
    yield
    store.reset_store()


@pytest.fixture
def client():
    return TestClient(app)


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


# members and admin in workspace A
@pytest.fixture
def auth_alice():
    return _auth("tok-alice")


@pytest.fixture
def auth_bob():
    return _auth("tok-bob")


@pytest.fixture
def auth_carol():
    # admin of workspace A
    return _auth("tok-carol")


# member in workspace B
@pytest.fixture
def auth_dave():
    return _auth("tok-dave")
