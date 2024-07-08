from __future__ import annotations

from weakref import WeakKeyDictionary
from base64 import b64encode

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mqga.connection.api.client import APIClient
    from mqga.q.message import IDUser
    from mqga.q.message import Emoji, ChannelAndMessageID
    from mqga.q.api import WSURL
    from mqga.q.api import FileInfo
    from mqga.q.api import RepliedMessage
    from mqga.q.api import MarkdownTemplate, MarkdownCustom, KeyboardTemplate, KeyboardCustom
    from mqga.q.constant import InteractionResult
    from mqga.q.payload import ButtonInteractEventPayload
    
    import httpx
    UseClientDefault = httpx._client.UseClientDefault

from mqga.log import log
from mqga.q.message import Message, ChannelMessage
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

    async def _get_source(self, api: str, params: dict | None = None, timeout: float | UseClientDefault = httpx.USE_CLIENT_DEFAULT, **kw):
        """ 加上渠道的 api 前缀 """
        return await self.client._get(f"{self.Prefix}{api}", params=params, timeout=timeout, **kw)

    async def _post_source(self, api: str, json: dict | None = None, timeout: float | UseClientDefault = httpx.USE_CLIENT_DEFAULT, **kw):
        """ 加上渠道的 api 前缀 """
        return await self.client._post(f"{self.Prefix}{api}", json=json, timeout=timeout, **kw)

    async def _put_source(self, api: str, json: dict | None = None, timeout: float | UseClientDefault = httpx.USE_CLIENT_DEFAULT, **kw):
        """ 加上渠道的 api 前缀 """
        return await self.client._put(f"{self.Prefix}{api}", json=json, timeout=timeout, **kw)

    async def _delete_source(self, api: str, params: dict | None = None, timeout: float | UseClientDefault = httpx.USE_CLIENT_DEFAULT, **kw):
        """ 加上渠道的 api 前缀 """
        return await self.client._delete(f"{self.Prefix}{api}", params=params, timeout=timeout, **kw)

    async def ws_url(self) -> str:
        """ 获取 ws 连接地址 """
        rj: WSURL = await self._get("/gateway")
        return rj["url"]

    @staticmethod
    def _payload_to_id(payload: EventPayload) -> str | None:
        """ 从 payload 中获取当前渠道的 id """
        return None

    @classmethod
    def _to_id(cls, payload: EventPayload | str) -> str:
        if isinstance(payload, EventPayload) and (_id := cls._payload_to_id(payload)):
            return _id 
        elif isinstance(payload, str):
            return payload
        raise NotImplementedError(f"尚未实现将 {payload!r} 转换为 {cls.__name__} 的 id")

    @classmethod
    def _message_data(cls, content: str, payload: EventPayload, type: MessageType, _sequence = 1):
        data = {"content": content}
        cls._message_type_data(data, type)
        cls._reply_id_data(data, payload)
        cls._message_sequence_data(data, payload, _sequence)
        return data

    @staticmethod
    def _message_type_data(data: dict, _type: MessageType):
        data["msg_type"] = _type
        return data

    @staticmethod
    def _reply_id_data(data: dict, payload: EventPayload):  
        if isinstance(payload.data, Message):
            data["msg_id"] = payload.data.id
        else:
            if not payload.id:
                raise ValueError(f"无法回复 {payload!r}，它既不是消息，也没有事件 ID")
            data["event_id"] = payload.id  # TODO 确定所有能回复的 payload 类型
            # 目前好像是用 payload 最外面的 id
            # getattr(payload.data, "id")
            # (payload.id.split(":")[-1] if payload.id else None)
        return data

    @staticmethod
    def _message_media_data(data: dict, media: FileInfo | None = None):
        if media:
            data["media"] = media
        return data

    _sequences: WeakKeyDictionary[EventPayload, int] = WeakKeyDictionary()

    @classmethod
    def _message_sequence_data(cls, data: dict, payload: EventPayload, _sequence = 1):
        """ 缓存对当前 payload 发过消息的次数（+1） """
        _sequence = cls._sequences.get(payload, _sequence)
        # log.debug(f"[{len(cls._sequences)}] {id(payload)}  {getattr(payload.data, 'content')}  {_sequence = }")
        if _sequence != 1:
            data["msg_seq"] = _sequence
        cls._sequences[payload] = _sequence + 1
        return data

    async def reply_text(self, payload: EventPayload, content: str) -> RepliedMessage:  # TODO 调整 content 和 payload 的顺序
        """ 以文本回复消息、事件 """
        return await self._post_source(f"/{self._to_id(payload)}/messages", json=self._message_data(
            content=content,
            payload=payload,
            type=MessageType.Text,  # TODO 其它消息类型
        ))

    async def file(self, payload_or_id: EventPayload | str, file_or_url: str | bytes, file_type: FileType = FileType.图片, send=False) -> FileInfo:
        """ 
        获取文件信息，用于发送富媒体消息

        source_id  渠道 id\\
        url  文件链接\\
        file_type  文件类型\\
        send = True 占用主动消息频次
        """
        data = {
            "file_type": file_type,
            # "url": url,
            "srv_send_msg": send
            # "file_data":  暂未支持 / base64?
        }
        if isinstance(file_or_url, bytes):
            data["file_data"] = b64encode(file_or_url).decode("ascii")
        elif isinstance(file_or_url, str):
            data["url"] = file_or_url
        return await self._post_source(f"/{self._to_id(payload_or_id)}/files", json=data)

    async def reply_media(self, payload: EventPayload, file_or_url: str | FileInfo | bytes, content: str = "", file_type: FileType = FileType.图片) -> RepliedMessage:
        """ 以富媒体（图文等）回复消息、事件 """
        source_id = self._to_id(payload)
        if isinstance(file_or_url, (str, bytes)):  # url 或 本地文件
            file_or_url = await self.file(source_id, file_or_url, file_type)
        data = self._message_data(content=content, payload=payload, type=MessageType.Media)
        data = self._message_media_data(data, file_or_url)
        return await self._post_source(f"/{source_id}/messages", json=data)
    
    # @staticmethod
    # def _md_data(template: str, params: dict[str, str] = None, content: str = "") -> MarkdownTemplate | MarkdownContent:
    #     if content:
    #         if template:
    #             log.warning(f"指定了原生 markdown 内容 {content = !r}, 将忽略模板 ID {template!r} 和参数 {params = !r}")
    #         return {"content": content}
    #     params = params or {}
    #     return {
    #         "custom_template_id": template,
    #         "params": [
    #             {"key": k, "values": [v]} for k, v in params.items()
    #         ]
    #     }

    @staticmethod
    def _message_md_data(data: dict, markdown: MarkdownTemplate | MarkdownCustom | None = None):
        if markdown:
            data["markdown"] = markdown
        return data

    @staticmethod
    def _message_keyboard_data(data: dict, keyboard: KeyboardTemplate | KeyboardCustom | None = None):
        if keyboard:
            data["keyboard"] = keyboard
        return data

    async def reply_md(self, payload: EventPayload, markdown: MarkdownTemplate | MarkdownCustom | None = None, keyboard: KeyboardTemplate | KeyboardCustom | None = None)  -> RepliedMessage:
        """ 
            以 markdown 回复消息、事件\n
            keyboard 为消息底部挂载的按钮
        """
        data = self._message_data(content="", payload=payload, type=MessageType.Markdown)
        # md = self._md_data(template, params, content)
        self._message_md_data(data, markdown)
        self._message_keyboard_data(data, keyboard)
        return await self._post_source(f"/{self._to_id(payload)}/messages", json=data)

    async def button_interacted(self, payload: ButtonInteractEventPayload, result: InteractionResult) -> bool:
        """ 向 QQ 告知按钮交互带来的 `payload` 事件已处理，结果为 `result`  """
        return await self._put(f"/interactions/{payload.data.id}", json={ "code": result })


class ChannelAPI(UnifiedAPI):

    Prefix = "/channels"

    @staticmethod
    def _payload_to_id(payload) -> str | None:
        """ 从 payload 中获取频道 id """
        return getattr(payload.data, "channel_id", None)

    @staticmethod
    def _message_type_data(data: dict, _type: MessageType):
        return data  # channel 不用这个
    
    @classmethod
    def _reply_id_data(cls, data: dict, payload: EventPayload):
        data = super()._reply_id_data(data, payload)
        if "msg_id" not in data:
            log.warning(f"{payload!r} 未能为 {data!r} 提供消息 ID，可能导致消息按主动消息而非回复消息发送")
        return data

    @classmethod
    def _message_sequence_data(cls, data: dict, payload: EventPayload, _sequence = 1):
        return data  # channel 不用这个

    async def reply_text(self, payload: EventPayload, content: str):
        return ChannelMessage(**await super().reply_text(payload, content))

    @staticmethod
    def _message_media_data(data: dict, media: str | bytes | None = None):
        if media:
            if isinstance(media, str):
                data["image"] = media
            elif isinstance(media, bytes):
                data["files"] = {"file_image": media}
        return data

    async def reply_media(self, payload: EventPayload, file_or_url: str | bytes, content: str = "", file_type: FileType = FileType.图片):
        """ 
            以图文回复消息、事件 
            
            频道中 file_or_url 只能是 url(`str`)， file_type 固定为 FileType.图片
        """
        # 频道不需要用 await self.file 拿到 FileInfo
        data = self._message_data(content=content, payload=payload, type=MessageType.Media)
        data = self._message_media_data(data, file_or_url)
        return ChannelMessage(**await self._post_source(f"/{self._to_id(payload)}/messages", files = data.pop("files", None), json=data))

    async def reply_md(self, payload: EventPayload, md: MarkdownTemplate | MarkdownCustom | None = None, keyboard: KeyboardTemplate | KeyboardCustom | None = None):
        return ChannelMessage(**await super().reply_md(payload, md, keyboard))  # 好像目前频道无法用被动消息回复 markdown

    def _reaction_url(self, message: ChannelAndMessageID, emoji: Emoji):
        if hasattr(message, "id"):
            return f"/{message.channel_id}/messages/{message.id}/reactions/{emoji.type}/{emoji.id}"
        return f"/{message.channel_id}/messages/{message.target.id}/reactions/{emoji.type}/{emoji.id}"

    async def reaction(self, message: ChannelAndMessageID, emoji: Emoji) -> bool:
        """ 对频道消息贴表情 """
        return await self._put_source(self._reaction_url(message, emoji))

    async def reaction_delete(self, message: ChannelAndMessageID, emoji: Emoji) -> bool:
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
        if users := result.get("users"):
            yield [User(**user) for user in users]
        while not result["is_end"]:
            data["cookie"] = result["cookie"]
            result = await self._get_source(url, data)
            if users := result.get("users"):
                yield [User(**user) for user in users]

    async def reaction_get_head_users(self, message: ChannelAndMessageID, emoji: Emoji, limit = 20):
        """ 获取对消息贴表情的用户，最多只能得到前 20 个 """
        return await anext(self.reaction_get_users_gen(message, emoji, limit))

class GroupAPI(UnifiedAPI):

    Prefix = "/v2/groups"

    @staticmethod
    def _payload_to_id(payload) -> str | None:
        """ 从 payload 中获取群 id """
        return getattr(payload.data, "group_id", None)

class PrivateAPI(UnifiedAPI):

    Prefix = "/v2/users"

    @staticmethod
    def _payload_to_id(payload) -> str | None:
        """ 从 payload 中获取用户 id """
        user: IDUser | None = getattr(payload.data, "author", None)
        return user and user.id
