from typing import Union, Literal, Any, List

from fastapi_pagination import LimitOffsetParams
from humps import camelize
from pydantic import BaseModel, Field

from app.config import NetworksEnum


class BalanceResult(BaseModel):
    balance: int


class BalanceRequest(BaseModel):
    address: str = Field(..., min_length=42, max_length=45)
    block_number: Union[Literal['latest'], int] = 'latest'
    network: NetworksEnum = NetworksEnum.AVAX


class EventsRequest(BaseModel):
    block_number: Union[Literal['latest'], int] = 'latest'


class EventsResponseItem(BaseModel):
    address: str
    block_hash: bytes
    block_number: int
    data: str
    log_index: int
    removed: bool
    topics: List[bytes]
    transaction_hash: bytes
    transaction_index: int

    class Config:
        alias_generator = lambda s: camelize(s)
        allow_population_by_field_name = True
        json_encoders = {
            bytes: lambda x: x.hex(),
            List[bytes]: lambda x: [e.hex() for e in x]
        }
