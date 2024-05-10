
from typing import Annotated, Literal
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

class IDUser(BaseModel):
    """ 有 ID 的用户 """
    id: str
    """ 用户 ID """

class User(IDUser):
    """ 有 ID 和用户名的用户 """
    username: str
    """ 用户名 """
    avatar: str | None = None
    """ 头像链接 """
    bot: bool | None = None
    """ 是机器人 """

class ChannelUser(User):
    """ 用户（全部信息） """
    union_openid: str | None = None
    """ 互联应用 OpenID """
    union_user_account: str | None = None
    """ 互联应用 用户信息 """

class PrivateIDUser(IDUser):
    """ 私聊用户 """
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="user_openid")
    """ 用户 openID """

class GroupIDUser(IDUser):
    """ 群成员 """
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="member_openid")
    """ 群成员 openID """

class UrlAttachment(BaseModel):  # MessageAttachment
    """ 有 url 的附件 """
    url: str
    """ 链接 """

class Attachment(UrlAttachment):
    """ 附件 """
    model_config = ConfigDict(populate_by_name=True)

    type: str = Field(alias="content_type")
    """ 附件类型 """
    filename: str
    """ 文件名 """
    width: str | int
    """ 宽 """
    height: str | int
    """ 高 """
    size: str | int
    """ 大小 """

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
    user: ChannelUser | None = None
    """ 用户信息 """
    nick: str
    """ 用户昵称 """
    roles: list[RoleID | str] # TODO 等文档更新后更新 RoleID
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
    author: IDUser
    """ 消息发送者 """
    content: str
    """ 消息内容 """
    timestamp: datetime
    """ 消息创建时间 """
    attachments: list[UrlAttachment] | None = None
    """ 附件列表 """

    def __hash__(self) -> int:
        return hash(self.id)

# class Message(BaseModel):
#     """ 消息 """
#     model_config = ConfigDict(populate_by_name=True)

#     id: str
#     """ 消息 ID """
#     # channel_id: str
#     # """ 子频道 ID """
#     # guild_id: str
#     # """ 频道 ID """
#     content: str
#     """ 消息内容 """
#     timestamp: datetime
#     """ 消息创建时间 """
#     # edited_timestamp: datetime | None = None
#     # """ 消息编辑时间 """
#     # mention_everyone: bool = False
#     # """ 是否 @ 全体 """
#     author: IDUser
#     """ 消息发送者 """
#     attachments: list[UrlAttachment] | None = None
#     """ 附件列表 """
#     # embeds: list[MessageEmbed] | None = None
#     # """ 嵌入内容？ """
#     # mentions: list[ChannelUser] | None = None
#     # """ @ 的人 """
#     # member: Member | None = None
#     # """ 消息发送者的成员信息 """
#     # ark: MessageArk | None = None
#     # """ Ark 消息 """
#     # seq: int = 0
#     # """ 子频道消息序列号（旧） """
#     # seq_in_channel: str
#     # """ 子频道消息序列号 """
#     # reference: MessageReference | None = Field(default=None, alias="message_reference")
#     # """ 引用的消息 """
#     # src_guild_id: str | None = None
#     # """ 私信消息来源频道的 ID """

class ChannelMessage(Message):
    """ 子频道消息 """
    channel_id: str
    """ 子频道 ID """
    guild_id: str
    """ 频道 ID """
    author: ChannelUser
    """ 消息发送者 """
    edited_timestamp: datetime | None = None
    """ 消息编辑时间 """
    mention_everyone: bool = False
    """ 是否 @ 全体 """
    embeds: list[MessageEmbed] | None = None
    """ 嵌入内容？ """
    mentions: list[ChannelUser] | None = None
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

class DirectMessage(ChannelMessage):
    """ 私信消息 """
    src_guild_id: str
    """ 私信消息来源频道的 ID """

class PrivateMessage(Message):
    """ 私聊消息 """
    author: PrivateIDUser
    """ 消息发送者 """
    attachments: list[Attachment] | None = None
    """ 附件列表 """

class GroupMessage(Message):
    """ 群聊消息 """
    author: GroupIDUser
    """ 消息发送者 """
    group_id: str = Field(alias="group_openid")
    """ 群 openID """
    attachments: list[Attachment] | None = None
    """ 附件列表 """

from mqga.q.constant import ReactionTargetType

class ReactionTarget(BaseModel):
    """ 表态目标 """
    id: str
    """ 表态目标 ID """
    type: ReactionTargetType | str
    """ 表态目标类型 """

from mqga.q.constant import EmojiType

class Emoji(BaseModel):
    """ 表情 """
    id: str
    """ QQ 表情 ID 或 emoji 本体 """
    type: EmojiType
    """ 表情类型 """

class MessageReaction(BaseModel):
    """ 对消息贴表情 """
    user_id: str
    """ 用户 ID """
    guild_id: str
    """ 频道 ID """
    channel_id: str
    """ 子频道 ID """
    target: ReactionTarget
    """ 表态目标 """
    emoji: Emoji
    """ 贴上的表情 """

ChannelAndMessageID = ChannelMessage | MessageReaction

from mqga.q.constant import InteractionType, ChatType
# from mqga.q.constant import InteractionScene

class ButtonData(BaseModel):
    """ 按钮数据 """
    model_config = ConfigDict(populate_by_name=True)

    data: str = Field(alias="button_data", default="")
    """ 按钮中附带的回调数据 `action.data` """
    id: str = Field(alias="button_id")
    """ 按钮 ID """

class ChannelButtonData(ButtonData):
    """ 频道中消息按钮的数据 """
    user_id: str
    """ 按钮交互者的 ID """
    message_id: str
    """ 按钮载体消息的 ID """

class PrivateMenuButtonData(ButtonData):
    """ 私聊快捷菜单数据 """
    feature_id: str
    """ 菜单按钮 ID """

# InteractionData
#   ButtonInteractionData
#       ChannelButtonInteractionData
#   MenuInteractionData

class InteractionData(BaseModel):
    """ 交互数据 """
    model_config = ConfigDict(populate_by_name=True)

    button: ButtonData = Field(alias="resolved")
    """ 按钮数据 """
    type: InteractionType = InteractionType.消息按钮
    """ 交互类型 """
    
class ButtonInteractionData(InteractionData):
    """ 消息按钮交互数据 """
    type: Literal[InteractionType.消息按钮] = InteractionType.消息按钮
    """ 交互类型 """

class ChannelButtonInteractionData(ButtonInteractionData):
    """ 频道中消息按钮的交互数据 """
    button: ChannelButtonData = Field(alias="resolved")
    """ 按钮数据 """

class MenuInteractionData(InteractionData):
    """ 私聊快捷菜单交互数据 """
    type: Literal[InteractionType.私聊快捷菜单] = InteractionType.私聊快捷菜单
    """ 交互类型 """
    button: PrivateMenuButtonData = Field(alias="resolved")
    """ 按钮数据 """

class ButtonInteraction(BaseModel):
    """ 按钮交互（被点击） """
    model_config = ConfigDict(populate_by_name=True)

    id: str
    """ 事件 ID """
    type: InteractionType = InteractionType.消息按钮
    """ 交互类型 """
    # scene: InteractionScene
    # """ 交互场景 """
    chat_type: ChatType
    """ 聊天场景 """
    data: InteractionData
    """ 交互数据 """
    version: int = 1
    """ 版本号 """
    application_id: str
    """ bot 的 AppID """

    @property
    def button(self):  # 避免 payload.data.data.button
        return self.data.button

class ChannelButtonInteraction(ButtonInteraction):
    """ 频道按钮交互 """
    type: Literal[InteractionType.消息按钮] = InteractionType.消息按钮
    """ 交互类型 """
    chat_type: Literal[ChatType.Guild] = ChatType.Guild
    """ 聊天场景 """
    guild_id: str
    """ 频道 ID """
    channel_id: str
    """ 子频道 ID """
    data: ChannelButtonInteractionData
    """ 交互数据 """

    @property
    def user_id(self) -> str:
        """ 按钮交互者的 ID """
        return self.data.button.user_id

    @property
    def message_id(self) -> str:
        """ 按钮载体消息的 ID """
        return self.data.button.message_id

class GroupButtonInteraction(ButtonInteraction):
    """ 群聊按钮交互 """
    type: Literal[InteractionType.消息按钮] = InteractionType.消息按钮
    """ 交互类型 """
    chat_type: Literal[ChatType.Group] = ChatType.Group
    """ 聊天场景 """
    group_id: str = Field(alias="group_openid")
    """ 群 openID """
    user_id: str = Field(alias="group_member_openid")
    """ 按钮交互者的 openID """
    data: ButtonInteractionData
    """ 交互数据 """

class PrivateButtonInteraction(ButtonInteraction):
    """ 私聊按钮交互 """
    chat_type: Literal[ChatType.Private] = ChatType.Private
    """ 聊天场景 """
    user_id: str = Field(alias="user_openid")
    """ 按钮交互者的 openID """
    data: Annotated[ButtonInteractionData | MenuInteractionData, Field(discriminator="type")]
    """ 交互数据 """

ButtonInteractionT = Annotated[ChannelButtonInteraction | GroupButtonInteraction | PrivateButtonInteraction, Field(discriminator="chat_type")]
