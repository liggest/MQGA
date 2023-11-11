from __future__ import annotations

import re
from typing import Callable, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from mqga.event.manager import DispatcherType
    from mqga.q.message import ChannelMessage

T = TypeVar("T", bound=Callable)

from mqga.event.box import Box
from mqga.event.event import Event, StrEvent
from mqga.event.dispatcher import Dispatcher, ChannelAtMessageDispatcher
from mqga.q.constant import EventType
from mqga.q.message import Emoji

def _deco_init(func: T):
    from mqga.lookup.context import context
    box = Box(func)
    return context, box

def _deco_init_dispatcher(func: T, cls: type[DispatcherType]):
    context, box = _deco_init(func)
    return context, box, context.bot._em.ensure(cls)
# class On:

#     def __call__(self, func: Callable[P, T]) -> Callable[P, T]:
#         return func

class OnChannelMessage:

    def __call__(self, func: Callable[[], str]):
        context, box, dispatcher = _deco_init_dispatcher(func, ChannelAtMessageDispatcher)
        dispatcher.register(context.bot, box)
        return func

    def full_match(self, content: str):
        def inner(func: Callable[[], str]):
            _, box, dispatcher = _deco_init_dispatcher(func, ChannelAtMessageDispatcher)
            parent = dispatcher._message_event
            event = parent.full_match_events.get(content) or StrEvent(f"qq_message_full_match_{content!r}", parent)
            event.register(box)
            parent.full_match_events.__setitem__(content, event)
            return func
        return inner
    
    def regex(self, content: str):
        def inner(func: Callable[[], str]):
            _, box, dispatcher = _deco_init_dispatcher(func, ChannelAtMessageDispatcher)
            parent = dispatcher._message_event
            event = StrEvent(f"qq_message_regex_{content!r}", parent)
            event.register(box)
            parent.regex_events.append((re.compile(content), event))
            return func
        return inner

    def filter_by(self, filter: Callable[[ChannelMessage], bool]):
        def inner(func: Callable[[], str]):
            _, box, dispatcher = _deco_init_dispatcher(func, ChannelAtMessageDispatcher)
            parent = dispatcher._message_event
            event = StrEvent(f"qq_message_filter_by_{filter!r}", parent)
            event.register(box)
            parent.filter_events.append((filter, event))
            return func
        return inner

on_channel_message = OnChannelMessage()

class OnEventPayload:

    def __call__(self, func: Callable[[], str]):
        context, box = _deco_init(func)
        context.bot._em._root_event.payload_event.event_payload_event.register(box)
        return func

    def of(self, type: EventType):
        if not (dispatcher_type := Dispatcher._subs.get(type)):
            raise ValueError(f"尚不支持处理 {type!r} 的事件")
        
        def inner(func: Callable[[], Emoji]):
            context, box, dispatcher = _deco_init_dispatcher(func, dispatcher_type)
            dispatcher: Dispatcher
            parent = context.bot._em._root_event.payload_event.event_payload_event
            payload_type = dispatcher._payload_type
            event = parent.of(payload_type) or Event[[], Emoji](f"event_payload_{payload_type!r}", parent)
            event.register(box)
            parent.event_events.__setitem__(payload_type, event)
            return func
        
        return inner

on_event = OnEventPayload()

# @on_channel_message.full_match("hello")
# def on_message_default():
#     return "Hello World!"

