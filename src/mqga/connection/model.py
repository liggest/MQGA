
from typing import Annotated, Literal, Any

from pydantic import BaseModel, Field, TypeAdapter

from mqga.connection.constant import OpCode, Intents, EventType

class Payload(BaseModel):
    op: OpCode
    """ 操作码 """

class HelloData(BaseModel):
    heartbeat_interval: int

class HelloPayload(Payload):
    op: Literal[OpCode.Hello] = OpCode.Hello
    d: HelloData
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
    op: Literal[OpCode.Identify] = OpCode.Identify
    d: IdentifyData
    """ 数据 """

class EventPayload(Payload):
    op: Literal[OpCode.Dispatch] = OpCode.Dispatch
    s: int
    """ 序列号 """
    t: EventType
    """ 事件类型 """
    d: dict
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
    t: Literal[EventType.WSReady] = EventType.WSReady
    d: ReadyData

class HeartbeatPayload(Payload):
    op: Literal[OpCode.Heartbeat] = OpCode.Heartbeat
    d: int | None
    """ 序列号 """

class HeartbeatAckPayload(Payload):
    op: Literal[OpCode.HeartbeatACK] = OpCode.HeartbeatACK

class ResumeData(BaseModel):
    token: str
    session_id: str
    seq: int

class ResumePayload(Payload):
    op: Literal[OpCode.Resume] = OpCode.Resume
    d: ResumeData

class ResumedEventPayload(EventPayload):
    t: Literal[EventType.WSResumed] = EventType.WSResumed
    d: str



EventPayloads = ReadyEventPayload | ResumedEventPayload

EventPayloadsAnnotation = Annotated[EventPayloads, Field(discriminator="t")]

ReceivePayloads = HelloPayload | HeartbeatAckPayload | EventPayloadsAnnotation

ReceivePayloadsAnnotation = Annotated[ReceivePayloads, Field(discriminator="op")]

ReceivePayloadsType = TypeAdapter(ReceivePayloadsAnnotation)
