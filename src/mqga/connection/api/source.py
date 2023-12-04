from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mqga.connection.api.client import APIClient
    from mqga.q.message import IDUser
    from mqga.q.message import Emoji, ChannelAndMessageID
    from mqga.q.api import WSURL
    from mqga.q.api import FileInfo

from mqga.q.message import Message
from mqga.q.message import User
from mqga.q.constant import MessageType, FileType
from mqga.q.payload import EventPayload

import httpx

class UnifiedAPI:
    """ 调用各种官方接口的通用逻辑 """

    Prefix = ""
    """ 渠道 api 前缀 """

    def __init__(self, client: APIClient):
        self.client = client

    @property
    def _get(self):
        return self.client._get
    
    @property
    def _post(self):
        return self.client._post
    
    @property
    def _put(self):
        return self.client._put
    
    @property
    def _delete(self):
        return self.client._delete

    async def _get_source(self, api: str, params: dict = None, timeout: float = httpx.USE_CLIENT_DEFAULT, **kw):
        """ 加上渠道的 api 前缀 """
        return await self.client._get(f"{self.Prefix}{api}", params=params, timeout=timeout, **kw)

    async def _post_source(self, api: str, data: dict = None, timeout: float = httpx.USE_CLIENT_DEFAULT, **kw):
        """ 加上渠道的 api 前缀 """
        return await self.client._post(f"{self.Prefix}{api}", data=data, timeout=timeout, **kw)

    async def _put_source(self, api: str, data: dict = None, timeout: float = httpx.USE_CLIENT_DEFAULT, **kw):
        """ 加上渠道的 api 前缀 """
        return await self.client._put(f"{self.Prefix}{api}", data=data, timeout=timeout, **kw)

    async def _delete_source(self, api: str, params: dict = None, timeout: float = httpx.USE_CLIENT_DEFAULT, **kw):
        """ 加上渠道的 api 前缀 """
        return await self.client._delete(f"{self.Prefix}{api}", params=params, timeout=timeout, **kw)

    async def ws_url(self) -> str:
        """ 获取 ws 连接地址 """
        rj: WSURL = await self._get("/gateway")
        return rj["url"]

    @classmethod
    def _to_id(cls, payload: EventPayload | str) -> str:
        """ 从 payload 中获取当前渠道的 id """
        if isinstance(payload, str):
            return payload
        raise NotImplementedError(f"尚未实现将 {payload!r} 转换为 {cls.__name__} 的 id")

    @staticmethod
    def _message_type_data(_type: MessageType):
        return {"msg_type": _type}

    @staticmethod
    def _reply_id(payload: EventPayload):
        if isinstance(payload.data, Message):
            return {"msg_id": payload.data.id}
        return {"event_id": payload.type}  # TODO event_id

    async def reply_text(self, content: str, payload: EventPayload):
        """ 以文本回复消息、事件 """
        return await self._post_source(f"/{self._to_id(payload)}/messages", data={
            "content": content,
            **self._message_type_data(MessageType.Text),  # TODO 其它消息类型
            **self._reply_id(payload)
        })

    async def file(self, payload_or_id: EventPayload | str, url: str, file_type: FileType = FileType.图片, send=False) -> FileInfo:
        """ 
        获取文件信息，用于发送富媒体消息

        source_id  渠道 id\\
        url  文件链接\\
        file_type  文件类型\\
        send = True 占用主动消息频次
        """
        return await self._post_source(f"/{self._to_id(payload_or_id)}/files", data={
            "file_type": file_type,
            "url": url,
            "srv_send_msg": send
            # "file_data":  暂未支持
        })

    async def reply_media(self, content: str, file_or_url: str | FileInfo, payload: EventPayload, file_type: FileType = FileType.图片):
        """ 回复群消息、事件 """
        source_id = self._to_id(payload)
        if isinstance(file_or_url, str):
            file_or_url = await self.file(source_id, file_or_url, file_type)
        return await self._post_source(f"/{source_id}/messages", data={
            "content": content,
            "media": file_or_url,
            **self._message_type_data(MessageType.Media),  # TODO 其它消息类型
            **self._reply_id(payload)
        })

class ChannelAPI(UnifiedAPI):

    Prefix = "/channels"

    @classmethod
    def _to_id(cls, payload: EventPayload | str) -> str:
        """ 从 payload 中获取频道 id """
        if isinstance(payload, EventPayload) and (channel_id := getattr(payload.data, "channel_id", None)):
            return channel_id
        return super()._to_id(payload)

    @staticmethod
    def _message_type_data(_type: MessageType):
        return {}  # channel 不用这个
    
    def _reaction_url(self, message: ChannelAndMessageID, emoji: Emoji):
        if hasattr(message, "id"):
            return f"/{message.channel_id}/messages/{message.id}/reactions/{emoji.type}/{emoji.id}"
        return f"/{message.channel_id}/messages/{message.target.id}/reactions/{emoji.type}/{emoji.id}"

    async def reaction(self, message: ChannelAndMessageID, emoji: Emoji):
        """ 对频道消息贴表情 """
        return await self._put_source(self._reaction_url(message, emoji))

    async def reaction_delete(self, message: ChannelAndMessageID, emoji: Emoji):
        """ 对频道消息揭表情 """
        return await self._delete_source(self._reaction_url(message, emoji))

    async def reaction_get_users_gen(self, message: ChannelAndMessageID, emoji: Emoji, per_page = 20):
        """ 获取对消息贴表情的用户 """
        if per_page > 50:
            raise ValueError(f"{per_page=}，应确保 20 <= per_page <= 50")
        url = self._reaction_url(message, emoji)
        data = {"limit": per_page}
        result = await self._get_source(url, data)
        data.clear()
        yield [User(**user) for user in result["users"]]
        while not result["is_end"]:
            data["cookie"] = result["cookie"]
            result = await self._get_source(url, data)
            yield [User(**user) for user in result["users"]]

    async def reaction_get_head_users(self, message: ChannelAndMessageID, emoji: Emoji, limit = 20):
        """ 获取对消息贴表情的用户，最多只能得到前 20 个 """
        return await anext(self.reaction_get_users_gen(message, emoji, limit))

class GroupAPI(UnifiedAPI):

    Prefix = "/v2/groups"

    @classmethod
    def _to_id(cls, payload: EventPayload | str) -> str:
        """ 从 payload 中获取群 id """
        if isinstance(payload, EventPayload) and (group_id := getattr(payload.data, "group_id", None)):
            return group_id
        return super()._to_id(payload)

class PrivateAPI(UnifiedAPI):

    Prefix = "/v2/users"

    @classmethod
    def _to_id(cls, payload: EventPayload | str) -> str:
        """ 从 payload 中获取用户 id """
        if isinstance(payload, EventPayload) and (user := getattr(payload.data, "author", None)):
            user: IDUser
            return user.id
        return super()._to_id(payload)