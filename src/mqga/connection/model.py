
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
    data: str = ""

class InvalidSessionPayload(Payload):
    op_code: Literal[OpCode.InvalidSession] = OpCode.InvalidSession
    data: bool = False

class ReconnectPayload(Payload):
    op_code: Literal[OpCode.Reconnect] = OpCode.Reconnect

class UnknownPayload(Payload):
    model_config = ConfigDict(extra="allow")

    op_code: OpCode
    seq_no: Optional[int] = None
    """ 序列号 """
    type: Optional[str] = None
    """ 事件类型 """
    data: Any = None
    """ 事件数据 """

from datetime import datetime

class User(BaseModel):
    """ 用户信息 """
    id: str
    """ 用户 ID """
    username: str
    """ 用户名 """
    avatar: str
    """ 头像链接 """
    bot: bool = False
    """ 是机器人 """
    union_openid: Optional[str] = None
    """ 互联应用 OpenID """
    union_user_account: Optional[str] = None
    """ 互联应用 用户信息 """

class MessageAttachment(BaseModel):
    """ 附件 """
    url: str
    """ 链接 """

class MessageEmbedThumbnail(BaseModel):
    """ 缩略图 """
    url: str
    """ 链接 """

class MessageEmbedField(BaseModel):
    """ 字段 """
    name: str
    """ 字段名 """

class MessageEmbed(BaseModel):
    title: str
    """ 标题 """
    prompt: Optional[str] = None
    """ 消息弹窗内容 """
    thumbnail: Optional[MessageEmbedThumbnail] = None
    """ 缩略图 """
    fields: Optional[list[MessageEmbedField]] = None
    """ 字段 """

from mqga.connection.constant import RoleID

class Role(BaseModel):
    """ 身份组 """
    id: RoleID
    """ 身份组 ID """
    name: str
    """ 身份组名 """
    color: Optional[int] = None
    """ 颜色（十六进制 ARGB 对应的十进制值） """
    hoist: Optional[bool] = None
    """ 展示在成员列表 """
    number: int
    """ 人数 """
    member_limit: int
    """ 人数上限 """

class Member(BaseModel):
    """ 成员 """
    user: Optional[User] = None
    """ 用户信息 """
    nick: str
    """ 用户昵称 """
    roles: list[RoleID | str] # TODO
    """ 身份组 ID 列表 """
    joined_at: datetime
    """ 加入时间 """

class MemberInGuild(Member):
    """ 频道成员 """
    guild_id: str
    """ 频道 ID """

class MessageArkObjectKVPair(BaseModel):
    """ 消息 ARK 对象数据的键值对 """
    key: str
    """ 键 """
    value: str
    """ 值 """

class MessageArkObject(BaseModel):
    """ 消息 ARK 对象数据 """
    kv_pair: list[MessageArkObjectKVPair] = Field(alias='obj_kv')
    """ 键值对 """

class MessageArkKVPair(MessageArkObjectKVPair):
    """ 消息 ARK 键值对 """
    obj: Optional[list[MessageArkObject]] = None
    """ 对象数据 """

class MessageArk(BaseModel):
    """ Ark 消息 """
    template_id: int
    """ 模板 ID """
    kv_pair: list[MessageArkKVPair] = Field(alias='kv')
    """ 键值对 """

class MessageReference(BaseModel):
    """ 消息引用 """
    message_id: str
    """ 被引用消息的 ID """
    ignore_error: bool = Field(default=False, alias="ignore_get_message_error")
    """ 获取被引用消息详情失败时，忽略错误 """

class Message(BaseModel):
    """ 消息 """
    model_config = ConfigDict(populate_by_name=True)

    id: str
    """ 消息 ID """
    channel_id: str
    """ 子频道 ID """
    guild_id: str
    """ 频道 ID """
    content: str
    """ 消息内容 """
    timestamp: datetime
    """ 消息创建时间 """
    edited_timestamp: Optional[datetime] = None
    """ 消息编辑时间 """
    mention_everyone: bool = False
    """ 是否 @ 全体 """
    author: User
    """ 消息发送者 """
    attachments: Optional[list[MessageAttachment]] = None
    """ 附件列表 """
    embeds: Optional[list[MessageEmbed]] = None
    """ 嵌入内容？ """
    mentions: Optional[list[User]] = None
    """ @ 的人 """
    member: Optional[Member] = None
    """ 消息发送者的成员信息 """
    ark: Optional[MessageArk] = None
    """ Ark 消息 """
    seq: int = 0
    """ 子频道消息序列号（旧） """
    seq_in_channel: str
    """ 子频道消息序列号 """
    reference: Optional[MessageReference] = Field(default=None, alias="message_reference")
    """ 引用的消息 """
    src_guild_id: Optional[str] = None
    """ 私信消息来源频道的 ID """

class ChannelAtMessageEventPayload(EventPayload):
    type: Literal[EventType.ChannelAtMessageCreate] = EventType.ChannelAtMessageCreate
    data: Message

EventPayloads = ReadyEventPayload | ResumedEventPayload | ChannelAtMessageEventPayload

EventPayloadsAnnotation = Annotated[EventPayloads, Field(discriminator="type")]

ReceivePayloads = EventPayloadsAnnotation | HeartbeatAckPayload | HelloPayload | InvalidSessionPayload | ReconnectPayload

ReceivePayloadsAnnotation = Annotated[ReceivePayloads, Field(discriminator="op_code")]

AllPayloads = ReceivePayloadsAnnotation # | UnknownPayload

ReceivePayloadsType = TypeAdapter(AllPayloads)

