
from pydantic import BaseModel, Field

from mqga.connection.constant import OpCode, Intents, EventType, Event

class Payload(BaseModel):
    op: OpCode
    """ 操作码 """

class HelloData(BaseModel):
    heartbeat_interval: int

class HelloPayload(Payload):
    op: OpCode = OpCode.Hello
    d: HelloData
    """ 数据 """

class IdentifyData(BaseModel):
    token: str
    intents: Intents
    shard: tuple[int, int] = (0, 1)
    properties: dict[str] = Field(default={
        "bot": False,
        "human": True,
        "0.1 + 0.2 ==": 0.1 + 0.2
    })

class IdentifyPayload(Payload):
    op: OpCode = OpCode.Identify
    d: IdentifyData
    """ 数据 """

class EventPayload(Payload):
    op: OpCode = OpCode.Dispatch
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
    t: Event.WS = Event.WS.Ready
    d: ReadyData

class HeartbeatPayload(Payload):
    op: OpCode = OpCode.Heartbeat
    d: int | None
    """ 序列号 """

class HeartbeatAckPayload(Payload):
    op: OpCode = OpCode.HeartbeatACK

class ResumeData(BaseModel):
    token: str
    session_id: str
    seq: int

class ResumePayload(Payload):
    op: OpCode = OpCode.Resume
    d: ResumeData

class ResumedEventPayload(EventPayload):
    t: Event.WS = Event.WS.Resumed
    d: str


