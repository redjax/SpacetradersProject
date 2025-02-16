from __future__ import annotations

from datetime import datetime
import json
import typing as t

import pendulum
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    computed_field,
    field_validator,
)

class RegisterAgentResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # created_at: pendulum.DateTime = Field(default_factory=pendulum.now)
    full_response: t.Union[bytes, dict] = Field(default=None)
    
    @field_validator("full_response")
    def validate_full_response(cls, v) -> bytes:
        if isinstance(v, bytes):
            return v
        elif isinstance(v, dict):
            _bytes: bytes = json.dumps(v).encode("utf-8")
            
            return _bytes
        else:
            raise ValidationError

    @computed_field
    @property
    def content_decode(self) -> dict:
        decoded: dict = json.loads(self.full_response)

        return decoded

    @computed_field
    @property
    def account_id(self) -> str:
        agent_account_id: str = self.content_decode["data"]["agent"]["accountId"]

        return agent_account_id

    @computed_field
    @property
    def symbol(self) -> str:
        agent_symbol: str = self.content_decode["data"]["agent"]["symbol"]

        return agent_symbol

    @computed_field
    @property
    def faction(self) -> str:
        agent_faction: str = self.content_decode["data"]["agent"]["startingFaction"]

        return agent_faction

    @computed_field
    @property
    def headquarters(self) -> str:
        agent_headquarters: str = self.content_decode["data"]["agent"]["headquarters"]

        return agent_headquarters

    @computed_field
    @property
    def token(self) -> str:
        agent_token: str = self.content_decode["data"]["token"]

        return agent_token


class RegisteredAgentBase(BaseModel):
    account_id: str = Field(default=None)
    symbol: str = Field(default=None)
    faction: str = Field(default=None)
    headquarters: str = Field(default=None)
    token: str = Field(default=None, repr=False)
    full_response: t.Union[dict, bytes] = Field(default=None, repr=False)
    
    @field_validator("full_response")
    def validate_full_response(cls, v) -> dict:
        if isinstance(v, dict):
            return v
        elif isinstance(v, bytes):
            _dict = json.loads(v)
            
            return _dict
        else:
            raise ValidationError
    

class RegisteredAgentIn(RegisteredAgentBase):
    pass


class RegisteredAgentOut(RegisteredAgentBase):
    agent_id: int
    
    created_at: str | datetime
    updated_at: str | datetime
