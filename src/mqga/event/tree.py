from functools import cached_property
from types import ModuleType
from collections import deque
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    import re
    from mqga.q.message import Message

from mqga.event.event import PlainEvent, StrEvent
from mqga.q.payload import Payload, EventPayload


# Root
#   Payload
#     type[Payload] : Event
#     EventPayload
#       type[EventPayload] : Event
#   Plugin
#     loading
#     init
#     stop
#     reload
#   Bot
#     init
#     stop
#   QQ
#     Message
#       FullMatch
#       Regexp

class RootEvent(PlainEvent):

    name = "root"

    @cached_property
    def payload_event(self):
        return PayloadEvent(parent = self)
    
    @cached_property
    def plugin_event(self):
        return PluginEvent(parent = self)

    @cached_property
    def bot_event(self):
        return BotEvent(parent = self)
    
    @cached_property
    def qq_event(self):
        return QQEvent(parent = self)

class PayloadEvent(PlainEvent):

    name = "payload"

    def __init__(self, parent: RootEvent = None):
        super().__init__(parent)
        self._payload_events: dict[type[Payload], PlainEvent] = None

    @property
    def payload_events(self):
        if self._payload_events is None:
            self._payload_events = {}
        return self._payload_events

    @cached_property
    def event_payload_event(self):
        event = EventPayloadEvent(parent = self)
        self.payload_events[EventPayload] = event
        return event
    
    def of(self, payload_type: type[Payload]):
        if self._payload_events:
            return self._payload_events.get(payload_type)

class EventPayloadEvent(PlainEvent):

    name = "event_payload"

    def __init__(self, parent: PayloadEvent = None):
        super().__init__(parent)
        self._event_events: dict[type[EventPayload], PlainEvent | StrEvent] = None

    @property
    def event_events(self):
        if self._event_events is None:
            self._event_events = {}
        return self._event_events
    
    def of(self, payload_type: type[EventPayload]):
        if self._event_events:
            return self._event_events.get(payload_type)

class PluginEvent(PlainEvent):

    name = "plugin"

    def __init__(self, parent: RootEvent = None):
        super().__init__(parent)
        self._plugin_events: dict[ModuleType, SinglePluginEvent] = None

    @property
    def plugin_events(self):
        if self._plugin_events is None:
            self._plugin_events = {}
        return self._plugin_events

    @cached_property
    def loading_event(self):
        return PlainEvent(name = "plugin_loading", parent = self)

    @cached_property
    def init_event(self):
        return PlainEvent(name = "plugin_init", parent = self)

    @cached_property
    def stop_event(self):
        return PlainEvent(name = "plugin_stop", parent = self)

    @cached_property
    def unload_event(self):
        return PlainEvent(name = "plugin_unload", parent = self)

class BotEvent(PlainEvent):

    name = "bot"

    @cached_property
    def init_event(self):
        return PlainEvent(name = "bot_init", parent = self)

    @cached_property
    def stop_event(self):
        return PlainEvent(name = "bot_stop", parent = self)

class QQEvent(PlainEvent):
    name = "qq"

    @cached_property
    def message_event(self):
        return MessageEvent(parent = self)

class SinglePluginEvent(PlainEvent):

    parent: PluginEvent

    def __init__(self, plugin: ModuleType, parent: PluginEvent = None):
        super().__init__(parent)
        self._plugin = plugin
        self.name = plugin.__name__

    @cached_property
    def loading_event(self):
        return PlainEvent(name = f"plugin_loading_{self.name}", parent = self.parent.loading_event)

    @cached_property
    def init_event(self):
        return PlainEvent(name = f"plugin_init_{self.name}", parent = self.parent.init_event)

    @cached_property
    def stop_event(self):
        return PlainEvent(name = f"plugin_stop_{self.name}", parent = self.parent.stop_event)

    @cached_property
    def unload_event(self):
        return PlainEvent(name = f"plugin_unload_{self.name}", parent = self.parent.unload_event)

class MessageEvent(StrEvent):

    name = "qq_message"

    def __init__(self, parent: QQEvent = None):
        super().__init__(parent)
        
        self._full_match_events: dict[str, StrEvent] = None
        self._regex_events: deque[tuple[re.Pattern, StrEvent]] = None
        self._filter_events: deque[tuple[Callable[[Message], bool], StrEvent]] = None

    @property
    def full_match_events(self):
        if self._full_match_events is None:
            self._full_match_events = {}
        return self._full_match_events

    @property
    def regex_events(self):
        if self._regex_events is None:
            self._regex_events = deque()
        return self._regex_events

    @property
    def filter_events(self):
        if self._filter_events is None:
            self._filter_events = deque()
        return self._filter_events
