from datetime import datetime
from enum import Enum

from pydantic import BaseModel, StrictInt, StrictStr


class ChatStatus(int, Enum):
    ERROR = -1
    SUCCESS = 1


class ChatRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatContext(BaseModel):
    chatroom_id: StrictInt
    role: ChatRole
    content: StrictStr


class ChatRequest(BaseModel):
    context: ChatContext
    timestamp: StrictInt


class ChatResponse(BaseModel):
    status: ChatStatus
    context: ChatContext
    status_detail: StrictStr
    timestamp: StrictInt = int(datetime.now().timestamp())
