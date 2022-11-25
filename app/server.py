import asyncio
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Request, APIRouter
from sse_starlette import EventSourceResponse

from app.core import get_wallet_balance, get_contract_events
from app.models import BalanceResult, BalanceRequest, EventsRequest, EventsResponseItem
from app.utils import log

r = APIRouter()


def start_app() -> FastAPI:
    app = FastAPI()
    app.include_router(r)
    return app


@r.get("/balance", response_model=BalanceResult)
async def balance(b_req: BalanceRequest = Depends()):
    try:
        b = await get_wallet_balance(b_req)
        return BalanceResult(balance=b)
    except Exception as e:
        log.error(f'For {b_req} have error.')
        log.exception(e)
        raise HTTPException(status_code=500, detail=f"Can't calculate balance: {e}")


@r.get("/events", response_model=List[EventsResponseItem])
async def contract_events(request: Request, e_req: EventsRequest = Depends()):
    try:
        async def gen():
            c = 0
            async for el in get_contract_events(e_req):
                if await request.is_disconnected():
                    break
                c += 1
                yield {
                    "event": "contract_event",
                    "id": c,
                    "data": el
                }

        return EventSourceResponse(gen())
    except Exception as e:
        log.error(f'For {e_req} have error.')
        log.exception(e)
        raise HTTPException(status_code=500, detail=f"Can't retrieve events of contract: {e}")
