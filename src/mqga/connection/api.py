from __future__ import annotations

from functools import cached_property
import asyncio
import time

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mqga.bot import Bot
    from mqga.q.payload import EventPayloadWithChannelID
    from mqga.q.message import Emoji, ChannelAndMessageID

import httpx

from mqga import LEGACY
from mqga.log import log
from mqga.q.payload import ChannelAtMessageEventPayload
from mqga.q.message import Message, ChannelMessage, MessageReaction
from mqga.q.message import User

class APIError(Exception):

    def __init__(self, data: dict):
        self._data = data
        if message := self.message:
            super().__init__(self.code, message)
        else:
            super().__init__(self.code)

    @property
    def code(self):
        return self._data["code"]

    @property
    def message(self):
        return self._data.get("message")


class API:

    def __init__(self, bot: Bot):
        self.bot = bot

        self._token = ""
        self._expire_time = 0
        self._fetch_time = 0

        self._client: httpx.AsyncClient = None

    if LEGACY:
        @property
        def _authorization(self):
            return f"Bot {self.bot.APPID}.{self.bot.APP_TOKEN}"

        @cached_property
        def header(self):
            return {"Authorization": self._authorization}
    else:
        @property
        def _authorization(self):
            return f"QQBot {self._token}"

        @cached_property
        def header(self):
            return {
                "Authorization": self._authorization,
                "X-Union-Appid": f"{self.bot.APPID}"
            }

    @cached_property
    def _token_data(self):
        return {
            "appId": f"{self.bot.APPID}",
            "clientSecret": f"{self.bot.APP_SECRET}",
        }

    @cached_property
    def _token_task(self):
        return asyncio.create_task(self._fetch_token())

    @property
    async def token(self):
        await self._ensure_token()
        return self._token

    if LEGACY:
        @cached_property
        def _base_url(self):
            return (r"https://api.sgroup.qq.com/", r"https://sandbox.api.sgroup.qq.com")[self.bot.in_sandbox]
    else:
        @cached_property
        def _base_url(self):
            return r"https://api.sgroup.qq.com/"

    async def _get(self, api: str, params: dict = None, timeout: float = httpx.USE_CLIENT_DEFAULT, **kw):
        await self._ensure_token()
        return self._handle_response(await self._client.get(api, params=params, timeout=timeout, **kw))

    async def _post(self, api: str, data: dict = None, timeout: float = httpx.USE_CLIENT_DEFAULT, **kw):
        await self._ensure_token()
        return self._handle_response(await self._client.post(api, json=data, timeout=timeout, **kw))

    async def _put(self, api: str, data: dict = None, timeout: float = httpx.USE_CLIENT_DEFAULT, **kw):
        await self._ensure_token()
        return self._handle_response(await self._client.put(api, json=data, timeout=timeout, **kw))

    async def _delete(self, api: str, params: dict = None, timeout: float = httpx.USE_CLIENT_DEFAULT, **kw):
        await self._ensure_token()
        return self._handle_response(await self._client.delete(api, params=params, timeout=timeout, **kw))

    def _handle_response(self, response: httpx.Response):
        http_error = None
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            http_error = e
        if response.status_code == 204: # 无数据
            return True
        data: dict = response.json()
        if (data and "code" in data):
            if http_error:
                raise APIError(data) from http_error
            else:
                raise APIError(data)
        return data or response.is_success

    async def _ensure_token(self):
        if self._token:
            now = time.time()
            if now < self._fetch_time:  # 不用获取新的
                return self._token
            if now < self._expire_time:  # 需要获取新的，但老的也还能用，先把 task 创出来
                self._token_task  # 如果还没有的话，创建
                return self._token
        await self._token_task
        return self._token

    TOKEN_URL = r"https://bots.qq.com/app/getAppAccessToken"
    TOKEN_INTERVAL = 50

    async def _fetch_token(self):
        async with httpx.AsyncClient() as client:
            data = (await client.post(self.TOKEN_URL, json=self._token_data)).json()
        self._token, expire_time = data["access_token"], int(
            data["expires_in"])
        log.info(f"拿到了新访问符，{expire_time} 秒后要再拿 :(")
        self._expire_time = time.time() + expire_time
        self._fetch_time = self._expire_time - self.TOKEN_INTERVAL  # 过期前就获取新的
        del self.header
        del self._token_task  # 因为要跑完了，删掉自己的 task
        await self._new_client()  # 也换上新的 client
        # return expire_time

    # async def _token_loop(self):
    #     log.info("找企鹅要访问符去了")
    #     self.header = {}  # 一开始没有 token，所以也没有 header
    #     end = self.bot._ended
    #     try:
    #         while not end.is_set():
    #             async with self._new_client():  # 在 token 有效期间保持 client 对象  TODO: 效果待验证
    #                 await asyncio.sleep(self._sleep_time)

    #                 await self._token_task
    #     finally:
    #         self._token_task.cancel()
    #         log.debug("token loop 结束")

    async def _new_client(self):
        base_url = self._base_url or ""
        timeout = self.bot.TIMEOUT or httpx._config.DEFAULT_TIMEOUT_CONFIG
        old_client = self._client
        self._client = httpx.AsyncClient(
            base_url=base_url, timeout=timeout, headers=self.header)
        if old_client:
            await old_client.aclose()
        return self._client

    async def init(self):
        log.info("API 初始化")
        self.header = {}  # 一开始没有 token，所以也没有 header

    async def stop(self):
        if "_token_task" in self.__dict__:  # 有点丑，用来判断 _token_task 是否存在
            # 用 hasattr 的话，没有任务也会执行一遍创一个出来
            self._token_task.cancel()
        if self._client:
            await self._client.aclose()
        log.info("API 停止")

    async def __aenter__(self):
        # 并不在这里初始化，而是在 bot 初始化时初始化
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def ws_url(self) -> str:
        rj = await self._get("/gateway")
        return rj["url"]

    async def channel_reply(self, content: str, event: EventPayloadWithChannelID):  # TODO
        return Message(**await self._post(f"/channels/{event.data.channel_id}/messages", data={
            "content": content,
            **({"msg_id": event.data.id} if isinstance(event, ChannelAtMessageEventPayload) else {"event_id": event.type})
        }))

    def _channel_reaction_url(self, message: ChannelAndMessageID, emoji: Emoji):
        if isinstance(message, ChannelMessage):
            return f"/channels/{message.channel_id}/messages/{message.id}/reactions/{emoji.type}/{emoji.id}"
        return f"/channels/{message.channel_id}/messages/{message.target.id}/reactions/{emoji.type}/{emoji.id}"

    async def channel_reaction(self, message: ChannelAndMessageID, emoji: Emoji):
        return await self._put(self._channel_reaction_url(message, emoji))

    async def channel_reaction_delete(self, message: ChannelAndMessageID, emoji: Emoji):
        return await self._delete(self._channel_reaction_url(message, emoji))

    async def channel_reaction_get_users_gen(self, message: ChannelAndMessageID, emoji: Emoji, per_page = 20):
        if per_page > 50:
            raise ValueError(f"{per_page=}，应确保 20 <= per_page <= 50")
        url = self._channel_reaction_url(message, emoji)
        data = {"limit": per_page}
        result = await self._get(url, data)
        data.clear()
        yield [User(**user) for user in result["users"]]
        while not result["is_end"]:
            data["cookie"] = result["cookie"]
            result = await self._get(url, data)
            yield [User(**user) for user in result["users"]]

    async def channel_reaction_get_head_users(self, message: ChannelMessage | MessageReaction, emoji: Emoji, limit = 20): # 只能得到第一批
        return await anext(self.channel_reaction_get_users_gen(message, emoji, limit))
