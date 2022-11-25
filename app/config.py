import json
import os
from enum import Enum

import yaml
from pydantic import BaseModel

from app.utils import log


class ContractCFG(BaseModel):
    network: str
    address: str
    abi: str


class CFG(BaseModel):
    networks: dict
    contract: ContractCFG


def _check_cfg(cfg: CFG) -> bool:
    return len(cfg.networks) and (cfg.contract.network in cfg.networks.keys()) and json.loads(cfg.contract.abi)


def _load_cfg() -> CFG:
    fn = os.environ.get('BC_API_CFG_FILE', "config.yaml")
    try:
        with open(fn, 'r') as f:
            cfg = CFG(**yaml.safe_load(f))
        if not _check_cfg(cfg):
            raise Exception("Bad config")
        return cfg
    except Exception as e:
        log.error(f"Can't load yaml config from: {fn}")
        raise e


cfg = _load_cfg()
networks = cfg.networks


def _load_enum(nets):
    class NEnum(str, Enum):
        pass

    return NEnum("networks", {n: n for n, url in nets.items()})


NetworksEnum = _load_enum(networks)
