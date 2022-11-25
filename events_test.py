import json

import pytest
import sseclient
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.models import EventsResponseItem
from app.server import start_app


@pytest.fixture(scope="function")
def app():
    yield start_app()


@pytest.fixture
def anyio_backend():
    return 'asyncio'



