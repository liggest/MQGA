
from typing import Annotated, Literal, Any
import operator
from functools import reduce

from pydantic import BaseModel, Field, TypeAdapter, ConfigDict
from pydantic_core import PydanticUndefined

from mqga.q.constant import OpCode, Intents, EventType
from mqga.q.message import ChannelMessage, GroupMessage, PrivateMessage
from mqga.q.message import User
from mqga.q.message import MessageReaction

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

# class UserData(BaseModel):
#     id: str
#     username: str
#     bot: bool

class ReadyData(BaseModel):
    version: int
    session_id: str
    user: User
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
    data: str = ""

class InvalidSessionPayload(Payload):
    op_code: Literal[OpCode.InvalidSession] = OpCode.InvalidSession
    data: bool = False

class ReconnectPayload(Payload):
    op_code: Literal[OpCode.Reconnect] = OpCode.Reconnect

# class UnknownPayload(Payload):
#     model_config = ConfigDict(extra="allow")

#     op_code: OpCode
#     seq_no: int | None = None
#     """ 序列号 """
#     type: str | None = None
#     """ 事件类型 """
#     data: Any = None
#     """ 事件数据 """

class ChannelAtMessageEventPayload(EventPayload):
    type: Literal[EventType.ChannelAtMessageCreate] = EventType.ChannelAtMessageCreate
    data: ChannelMessage

class GroupAtMessageEventPayload(EventPayload):
    type: Literal[EventType.GroupAtMessageCreate] = EventType.GroupAtMessageCreate
    data: GroupMessage

class PrivateMessageEventPayload(EventPayload):
    type: Literal[EventType.PrivateMessageCreate] = EventType.PrivateMessageCreate
    data: PrivateMessage

class ChannelMessageReactionAddEventPayload(EventPayload):
    type: Literal[EventType.ChannelMessageReactionAdd] = EventType.ChannelMessageReactionAdd
    data: MessageReaction

class ChannelMessageReactionRemoveEventPayload(EventPayload):
    type: Literal[EventType.ChannelMessageReactionRemove] = EventType.ChannelMessageReactionRemove
    data: MessageReaction

# EventPayloads = ReadyEventPayload | ResumedEventPayload | ChannelAtMessageEventPayload

# EventPayloadsAnnotation = Annotated[EventPayloads, Field(discriminator="type")]

# ReceivePayloads = EventPayloadsAnnotation | HeartbeatAckPayload | HelloPayload | InvalidSessionPayload | ReconnectPayload

# ReceivePayloadsAnnotation = Annotated[ReceivePayloads, Field(discriminator="op_code")]

# AllPayloads = ReceivePayloadsAnnotation # | UnknownPayload

# ReceivePayloadsType = TypeAdapter(AllPayloads)

EventPayloadWithChannelID = (ChannelAtMessageEventPayload 
                             | ChannelMessageReactionAddEventPayload 
                             | ChannelMessageReactionRemoveEventPayload)  # TODO 还有更多

# from typing import Protocol

# class DataWithChannelID(Protocol):
#     channel_id: str

# class EventPayloadWithChannelID(Protocol):
#     op_code: Literal[OpCode.Dispatch] = OpCode.Dispatch
#     seq_no: int
#     """ 序列号 """
#     type: EventType
#     """ 事件类型 """
#     data: DataWithChannelID
#     """ 事件数据 """

def _event_payloads() -> type[ReadyEventPayload] | type[ResumedEventPayload] | type[EventPayload]:
    return Annotated[
        reduce(operator.or_, EventPayload.__subclasses__()),  # TODO 目前只支持 EventPayload 的直接子类
        Field(discriminator="type")
    ]

def _receive_payloads():
    return Annotated[
        HeartbeatAckPayload | HelloPayload | InvalidSessionPayload | ReconnectPayload | _event_payloads(), 
        Field(discriminator="op_code")
    ]

def receive_payloads_type():
    return TypeAdapter(_receive_payloads())

def op_code_from(payload_cls: type[Payload]) -> OpCode | None:
    if (code := payload_cls.model_fields["op_code"].default) is not PydanticUndefined:
        return code 

def event_type_from(payload_cls: type[EventPayload]) -> EventType | None:
    if (event_type := payload_cls.model_fields["type"].default) is not PydanticUndefined:
        return event_type 

def payload_cls_from(op_code: OpCode):
    if op_code == OpCode.Dispatch:
        return EventPayload
    if any(payload_type := cls for cls in Payload.__subclasses__() if op_code_from(cls) == op_code):
        return payload_type
    raise ValueError(f"没有对应 {op_code = } 的 Payload 子类")

def event_payload_cls_from(event_type: EventType):
    if any(payload_type := cls for cls in EventPayload.__subclasses__() if event_type_from(cls) == event_type):
        return payload_type
    raise ValueError(f"没有对应 {event_type = } 的 EventPayload 子类")
