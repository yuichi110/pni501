from typing import Any, Dict, List
from pydantic import BaseModel, validator


class LegacyOrderPayload(BaseModel):
    customer_id: str
    items: List[Dict[str, Any]]
    metadata: dict = {}
    legacy_flag = True  # type: ignore

    class Config:
        orm_mode = True

    @validator("customer_id")
    def check_customer(cls, val):
        return val.strip()
