
from typing import Annotated, Literal, Any, Optional

from pydantic import BaseModel, Field, TypeAdapter, ConfigDict

from mqga.connection.constant import OpCode, Intents, EventType

def _real_name(name: str):
    return {"op_code": "op", "data": "d", "seq_no": "s", "type": "t"}.get(name, name)

class Payload(BaseModel):
    model_config = ConfigDict(alias_generator=_real_name, populate_by_name=True)  
    # 可以用 Payload(op_code=...) 也可以用 Payload(op=...)

    op_code: OpCode
    """ 操作码 """

class HelloData(BaseModel):
    heartbeat_interval: int

class HelloPayload(Payload):
    op_code: Literal[OpCode.Hello] = OpCode.Hello
    data: HelloData
    """ 数据 """

class IdentifyData(BaseModel):
    token: str
    intents: Intents
    shard: tuple[int, int] = (0, 1)
    properties: dict[str, Any] = Field(default={
        "bot": False,
        "human": True,
        "0.1 + 0.2 ==": 0.1 + 0.2
    })

class IdentifyPayload(Payload):
    op_code: Literal[OpCode.Identify] = OpCode.Identify
    data: IdentifyData
    """ 数据 """

class EventPayload(Payload):
    op_code: Literal[OpCode.Dispatch] = OpCode.Dispatch
    seq_no: int
    """ 序列号 """
    type: EventType
    """ 事件类型 """
    data: dict
    """ 事件数据 """

class UserData(BaseModel):
    id: str
    username: str
    bot: bool

class ReadyData(BaseModel):
    version: int
    session_id: str
    user: UserData
    shard: tuple[int, int]

class ReadyEventPayload(EventPayload):
    type: Literal[EventType.WSReady] = EventType.WSReady
    data: ReadyData

class HeartbeatPayload(Payload):
    op_code: Literal[OpCode.Heartbeat] = OpCode.Heartbeat
    data: int | None
    """ 序列号 """

class HeartbeatAckPayload(Payload):
    op_code: Literal[OpCode.HeartbeatACK] = OpCode.HeartbeatACK

class ResumeData(BaseModel):
    token: str
    session_id: str
    seq: int

class ResumePayload(Payload):
    op_code: Literal[OpCode.Resume] = OpCode.Resume
    data: ResumeData

class ResumedEventPayload(EventPayload):
    type: Literal[EventType.WSResumed] = EventType.WSResumed
    data: str

class InvalidSessionPayload(Payload):
    op_code: Literal[OpCode.InvalidSession] = OpCode.InvalidSession
    data: Optional[bool]

EventPayloads = ReadyEventPayload | ResumedEventPayload

EventPayloadsAnnotation = Annotated[EventPayloads, Field(discriminator="type")]

ReceivePayloads = HelloPayload | HeartbeatAckPayload | InvalidSessionPayload | EventPayloadsAnnotation

ReceivePayloadsAnnotation = Annotated[ReceivePayloads, Field(discriminator="op_code")]

ReceivePayloadsType = TypeAdapter(ReceivePayloadsAnnotation)
