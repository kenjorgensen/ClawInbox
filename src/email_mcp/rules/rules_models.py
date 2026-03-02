from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class RuleField(str, Enum):
    subject = "subject"
    from_addr = "from_addr"
    to_addrs = "to_addrs"
    text = "text"


class RuleSpec(BaseModel):
    name: str
    field: RuleField
    pattern: str
    label: str
    enabled: bool = True
