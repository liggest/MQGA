from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mqga.bot import Bot

from mqga.lookup import _vars
from mqga.lookup.property import VarProperty

class BotContext:

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        _vars._last_ctx.set(self)
        _vars._last_bot.set(bot)

    message = VarProperty(_vars._message)
    payload = VarProperty(_vars._event_payload)

Context = BotContext

if TYPE_CHECKING:

    from mqga.q.message import ChannelMessage, GroupMessage

    class ChannelContext(BotContext):

        message: ChannelMessage

    class GroupContext(BotContext):

        message: GroupMessage

    context = _vars._last_ctx.get()
    channel_context: ChannelContext
    group_context: GroupContext

_context_names = {"context", "channel_context", "group_context"}

def _get_context():
    return _vars._last_ctx.get()

def __getattr__(name: str):
    if name in _context_names:
        return _get_context()
    raise AttributeError
