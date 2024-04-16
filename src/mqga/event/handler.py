from __future__ import annotations

import inspect

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mqga.bot import Bot
    from mqga.event.dispatcher import MessageDispatcher
    from mqga.q.payload import EventPayload

from mqga.q.message import Emoji
from mqga.q.constant import InteractionResult

async def handle_awaitable(dispatcher, result, bot: Bot, target) -> bool:
    if inspect.isawaitable(result):
        return bot._em.background_task(result)  # 回调返回的可等待对象，送去后台执行


async def handle_str(dispatcher: MessageDispatcher, result, bot: Bot, target) -> bool:
    if isinstance(result, str):
        return await dispatcher._reply_str(result, bot, target)

async def handle_emoji_add(dispatcher, result, bot: Bot, target: EventPayload):
    if isinstance(result, Emoji):
        return await bot._api.channel.reaction(target.data, result)

async def handle_emoji_remove(dispatcher, result, bot: Bot, target: EventPayload):
    if isinstance(result, Emoji):
        return await bot._api.channel.reaction_delete(target.data, result)

async def handle_button_interact(dispatcher, result, bot: Bot, target: EventPayload):
    if result is None:
        result = InteractionResult.操作成功      # 无返回值的情况下默认操作成功
    elif isinstance(result, bool):
        result = InteractionResult(not result)  # True => InteractionResult.操作成功  False => InteractionResult.操作失败
    if isinstance(result, (int, InteractionResult)):
        return await bot._api._unified_api.button_interacted(target, result)
