import json

import pytest
from httpx import AsyncClient

from app.config import NetworksEnum
from app.models import EventsResponseItem
from app.server import start_app


@pytest.fixture(scope="function")
def app():
    yield start_app()


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.mark.anyio
async def test_balance(app):
    test_vals = {'good': {"accounts": ["0x0716a17fbaee714f1e6ab0f9d59edbc5f09815c0",
                                       "0xbe0eb53f46cd790cd13851d5eff43d12404d33e8",
                                       "0x32b0419f98d189a43c1b583be88a87e9be517b73",
                                       "X-avax1hjpa6ctccwgd3qjeq8cp70ly50kne2ras5yavh",
                                       "P-avax1hjpa6ctccwgd3qjeq8cp70ly50kne2ras5yavh"],
                          "block_numbers": ["latest", 16030227, 10030227, 6030227, 0],
                          "networks": [n.value for n in NetworksEnum]},
                 'bad': {'accounts': ["", None, "test account",
                                      "0xbe0eb53f46cd790cd13851d5eff43d12404d33e71",
                                      "0xbe0eb53f46cd790cd13851d5eff43d12404d33e"],
                         'block_numbers': ["previous", "test"],
                         'networks': ["XXX", "test", None, ],
                         }
                 }

    def params_gen(name='good'):
        for acc in test_vals[name]['accounts']:
            for bn in test_vals[name]['block_numbers']:
                for n in test_vals[name]['networks']:
                    yield acc, bn, n

    async with AsyncClient(app=app, base_url="http://test") as ac:
        for acc, bn, n in params_gen('good'):
            resp = await ac.get("/balance", params={'address': acc, 'block_number': bn, 'network': n})
            data = resp.json()
            if resp.status_code == 200:
                assert "balance" in data
                assert isinstance(data['balance'], int)
            elif resp.status_code == 500:
                assert "detail" in data
            else:
                assert False, f"unsupported status: {resp.status_code}"

        for acc, bn, n in params_gen('bad'):
            resp = await ac.get("/balance", params={'address': acc, 'block_number': bn, 'network': n})
            assert resp.status_code == 422
            data = resp.json()
            assert "detail" in data


@pytest.mark.anyio
async def test_events(app):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        async with ac.stream(url="/events", method='GET', params={'block_number': 22739100}) as stream:
            event_name = ""
            async for chunk in stream.aiter_lines():
                if chunk.startswith("event"):
                    event_name = chunk[7:]
                elif chunk.startswith("data"):
                    if event_name == "contract_event":
                        data = json.loads(chunk[6:-1])
                        assert EventsResponseItem(**data), "result structure is invalid"
