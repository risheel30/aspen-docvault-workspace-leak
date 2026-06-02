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


@pytest.fixture
def auth_alice():
    return _auth("tok-alice")


@pytest.fixture
def auth_bob():
    return _auth("tok-bob")


@pytest.fixture
def auth_carol():
    return _auth("tok-carol")


@pytest.fixture
def auth_dave():
    return _auth("tok-dave")
