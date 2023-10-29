
from pydantic import BaseModel, Field, ConfigDict
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
    union_openid: str | None = None
    """ 互联应用 OpenID """
    union_user_account: str | None = None
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
    prompt: str | None = None
    """ 消息弹窗内容 """
    thumbnail: MessageEmbedThumbnail | None = None
    """ 缩略图 """
    fields: list[MessageEmbedField] | None = None
    """ 字段 """

from mqga.q.constant import RoleID

class Role(BaseModel):
    """ 身份组 """
    id: RoleID
    """ 身份组 ID """
    name: str
    """ 身份组名 """
    color: int | None = None
    """ 颜色（十六进制 ARGB 对应的十进制值） """
    hoist: bool | None = None
    """ 展示在成员列表 """
    number: int
    """ 人数 """
    member_limit: int
    """ 人数上限 """

class Member(BaseModel):
    """ 成员 """
    user: User | None = None
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
    obj: list[MessageArkObject] | None = None
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
    edited_timestamp: datetime | None = None
    """ 消息编辑时间 """
    mention_everyone: bool = False
    """ 是否 @ 全体 """
    author: User
    """ 消息发送者 """
    attachments: list[MessageAttachment] | None = None
    """ 附件列表 """
    embeds: list[MessageEmbed] | None = None
    """ 嵌入内容？ """
    mentions: list[User] | None = None
    """ @ 的人 """
    member: Member | None = None
    """ 消息发送者的成员信息 """
    ark: MessageArk | None = None
    """ Ark 消息 """
    seq: int = 0
    """ 子频道消息序列号（旧） """
    seq_in_channel: str
    """ 子频道消息序列号 """
    reference: MessageReference | None = Field(default=None, alias="message_reference")
    """ 引用的消息 """
    src_guild_id: str | None = None
    """ 私信消息来源频道的 ID """
