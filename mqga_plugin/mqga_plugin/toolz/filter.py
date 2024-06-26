from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Callable
    from mqga.lookup.context import BotContext

class Filter:

    def __init__(self, context: BotContext = None):
        if not context:
            from mqga.lookup.context import context
        self.context = context

    def __call__(self) -> bool:
        return False
    
    def __and__(self, other: Callable[[], bool]) -> AndFilter:
        if isinstance(other, Filter):
            return AndFilter(self, other)
        elif callable(other):
            return AndFilter(self, PlainFilter(other))
        return NotImplemented

    def __or__(self, other: Callable[[], bool]) -> OrFilter:
        if isinstance(other, Filter):
            return OrFilter(self, other)
        elif callable(other):
            return OrFilter(self, PlainFilter(other))
        return NotImplemented

    def __repr__(self) -> str:
        return self.__class__.__name__

class AndFilter(Filter):

    @classmethod
    def from_two(cls, one: Filter, *others: Filter):
        if isinstance(one, AndFilter):
            one.filters.extend(others)
            return one
        return AndFilter(one, *others)

    def __init__(self, *filters: Filter):
        self.filters = [*filters]

    def __call__(self) -> bool:
        return all(call() for call in self.filters)

    def __repr__(self) -> str:
        return " & ".join(repr(f) for f in self.filters)

class OrFilter(Filter):

    @classmethod
    def from_two(cls, one: Filter, *others: Filter):
        if isinstance(one, OrFilter):
            one.filters.extend(others)
            return one
        return OrFilter(one, *others)

    def __init__(self, *filters: Filter):
        self.filters = [*filters]

    def __call__(self) -> bool:
        return any(call() for call in self.filters)
    
    def __repr__(self) -> str:
        return " | ".join(repr(f) for f in self.filters)

class PlainFilter(Filter):

    def __init__(self, func: Callable[[], bool], context: BotContext = None):
        super().__init__(context)
        self.func = func

    def __call__(self) -> bool:
        return self.func()
    
    def __repr__(self) -> str:
        return f"{super().__repr__()}({self.func!r})"

class PrefixFilter(Filter):

    def __init__(self, prefix: str, ignore_case = True, context: BotContext = None):
        super().__init__(context)
        self.prefix = prefix
        self.ignore_case = ignore_case

    def __call__(self) -> bool:
        message = self.context.message.content.lstrip()
        if self.ignore_case:
            message = message.lower()
        self.context.matched << message
        return message.startswith(self.prefix)

    def __repr__(self) -> str:
        return f"{super().__repr__()}({self.prefix!r})"

class SuffixFilter(Filter):

    def __init__(self, suffix: str, ignore_case = True, context: BotContext = None):
        super().__init__(context)
        self.suffix = suffix
        self.ignore_case = ignore_case

    def __call__(self) -> bool:
        message = self.context.message.content.rstrip()
        if self.ignore_case:
            message = message.lower()
        self.context.matched << message
        return message.endswith(self.suffix)

    def __repr__(self) -> str:
        return f"{super().__repr__()}({self.suffix!r})"

class CommandFilter(Filter):

    prefix = "/"

    def __init__(self, command: str, ignore_case = False, context: BotContext = None):
        super().__init__(context)
        if ignore_case:
            command = command.lower()
        self.name = command.lstrip(self.prefix)
        self.ignore_case = ignore_case

    def __call__(self) -> bool:
        message = self.context.message.content.lstrip().lstrip(self.prefix)
        if self.ignore_case:
            message = message.lower()
        if is_match := message.startswith(self.name):
            message = message.removeprefix(self.name).lstrip()
        self.context.matched << message
        return is_match

    @property
    def command(self):
        return f"{self.prefix}{self.name}"

    def __repr__(self) -> str:
        return f"{super().__repr__()}({self.command!r})"

class Filters:

    prefix = PrefixFilter
    suffix = SuffixFilter
    command = CommandFilter
