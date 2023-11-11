from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mqga.bot import Bot
    from mqga.lookup.context import BotContext
    from mqga.q.payload import EventPayload
    from mqga.q.message import Message

from contextvars import ContextVar
    
_last_ctx: ContextVar[BotContext] = ContextVar("last_ctx", default=None)
_last_bot: ContextVar[Bot] = ContextVar("last_bot", default=None)

_event_payload: ContextVar[EventPayload] = ContextVar("_event_payload", default=None)
_message: ContextVar[Message] = ContextVar("message", default=None)

