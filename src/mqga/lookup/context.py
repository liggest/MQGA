from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, TypeVar
if TYPE_CHECKING:
    from mqga.bot import Bot
    from typing_extensions import Self
    T = TypeVar("T")

from mqga.lookup import _vars
from mqga.lookup.property import VarProperty

class BotContext:

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        _vars._last_ctx.set(self)
        _vars._last_bot.set(bot)

    message = VarProperty(_vars._message)
    payload = VarProperty(_vars._payload)

    @property
    def in_any(self) -> Self:
        """ 俺寻思这儿该跑任何渠道的代码吧？ """
        return self

    @property
    def in_channel(self) -> ChannelContext:
        """ 俺寻思这儿该跑频道的的代码吧？ """
        return self

    @property
    def in_group(self) -> GroupContext:
        """ 俺寻思这儿该跑群聊的代码吧？ """
        return self
    
    @property
    def in_private(self) -> PrivateContext:
        """ 俺寻思这儿该跑私聊的代码吧？ """
        return self

    @cached_property
    def matched(self):
        return Matched()

    # matched_regex = VarProperty(_vars._matched_regex)

Context = BotContext

class Matched:

    regex = VarProperty(_vars._matched_regex)
    filter_by = VarProperty(_vars._matched_filter_by, default=())

    def collect(self, result: T) -> T:
        """ 将 result 作为当前匹配的结果加入 matched.filter_by """
        self.filter_by = self.filter_by + (result,)
        return result
    
    __lshift__ = collect

if TYPE_CHECKING:

    from mqga.q.message import ChannelMessage, GroupMessage, PrivateMessage

    class ChannelContext(BotContext):

        message: ChannelMessage

    class GroupContext(BotContext):

        message: GroupMessage

    class PrivateContext(BotContext):

        message: PrivateMessage

    context = _vars._last_ctx.get()
    channel_context: ChannelContext
    group_context: GroupContext
    private_context: PrivateContext

_context_names = {"context", "channel_context", "group_context", "private_context"}

def _get_context():
    return _vars._last_ctx.get()

def __getattr__(name: str):
    if name in _context_names:
        return _get_context()
    raise AttributeError
