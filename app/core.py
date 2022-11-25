import asyncio
import json
from enum import Enum
from functools import partial
from typing import List

from eth_utils import event_abi_to_log_topic
from web3 import Web3
from web3._utils.events import get_event_data
from web3._utils.filters import construct_event_filter_params
from web3.eth import AsyncEth
from web3.middleware import async_geth_poa_middleware, geth_poa_middleware
from web3.net import AsyncNet

from app.config import networks, cfg
from app.models import BalanceRequest, EventsRequest, EventsResponseItem
from app.utils import log


def _init_async_web3(url: str) -> Web3:
    rpc = Web3(Web3.AsyncHTTPProvider(url),
               modules={'eth': AsyncEth, 'net': AsyncNet},
               middlewares=[])
    rpc.middleware_onion.inject(async_geth_poa_middleware, layer=0)
    return rpc


def _init_web3(url: str) -> Web3:
    rpc = Web3(Web3.HTTPProvider(url))
    rpc.middleware_onion.inject(geth_poa_middleware, layer=0)
    return rpc


async_rpcs = {n: _init_async_web3(url) for n, url in networks.items()}
w3 = _init_web3(networks[cfg.contract.network])


async def get_wallet_balance(b_request: BalanceRequest) -> int:
    w3 = async_rpcs[b_request.network]
    e_addr = Web3.toChecksumAddress(b_request.address)
    block = await w3.eth.get_block(b_request.block_number)
    return await w3.eth.get_balance(e_addr, block_identifier=block['number'])


contract = w3.eth.contract(address=Web3.toChecksumAddress(cfg.contract.address), abi=json.loads(cfg.contract.abi))
contract_event_abi = contract.events.Upgraded._get_event_abi()

block_count_buff = 500
event_batch_size = 100


def get_logs(from_block, to_block):
    # NB variant for `Upgraded` events only. Changes some structure.
    # data_filter_set, event_filter_params = construct_event_filter_params(
    #     contract_event_abi,
    #     rpc.codec,
    #     address=contract.address,
    #     argument_filters={'address': contract.address},
    #     fromBlock=from_block,
    #     toBlock=to_block
    # )
    # return [get_event_data(entry) e for e in rpc.eth.get_logs(event_filter_params)]
    return w3.eth.getLogs(dict(
        address=contract.address,
        fromBlock=from_block,
        toBlock=to_block
    ))


async def fetch_events(e_request: EventsRequest):
    loop = asyncio.get_running_loop()

    latest_block = w3.eth.get_block('latest').number
    for from_block in range(e_request.block_number, latest_block, block_count_buff):
        to_block = (from_block + block_count_buff) if (from_block + block_count_buff) < latest_block else latest_block
        logs = await loop.run_in_executor(None, partial(get_logs, from_block, to_block), )
        for entry in logs:
            yield entry


async def get_contract_events(e_request: EventsRequest):
    async for event in fetch_events(e_request):
        yield EventsResponseItem(**event).json()
