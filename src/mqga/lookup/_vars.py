from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mqga.bot import Bot
    from mqga.lookup.context import BotContext
    from mqga.q.payload import Payload, EventPayload
    from mqga.q.message import Message
    import re

from contextvars import ContextVar
    
_last_ctx: ContextVar[BotContext | None] = ContextVar("last_ctx", default=None)
_last_bot: ContextVar[Bot | None] = ContextVar("last_bot", default=None)

_payload: ContextVar[Payload | EventPayload | None] = ContextVar("payload", default=None)
_message: ContextVar[Message | None] = ContextVar("message", default=None)

_matched_regex: ContextVar[re.Match | None] = ContextVar("matched_regex", default=None)
_matched_filter_by: ContextVar[tuple] = ContextVar("matched_filter_by", default=())
