
from typing import List, Union

import pydantic
import yaml


class SMTPConfig(pydantic.BaseModel):
    server: str
    port: int
    ssl: Union[bool, None] = False
    username: str
    password: str


class SendTarget(pydantic.BaseModel):
    name: str
    email: str
    items: List[str]


class DiscountCheckerConfig(pydantic.BaseModel):
    smtp: SMTPConfig
    send_targets: List[SendTarget]


def load_config(path: str) -> DiscountCheckerConfig:
    config = DiscountCheckerConfig(**yaml.safe_load(open(path)))
    return config
