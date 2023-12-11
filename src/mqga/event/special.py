
import re
import asyncio
from typing import TYPE_CHECKING, AsyncGenerator, Callable

from mqga.event.event import RuleMultiEvent, PlainReturns

class RegexEvent(RuleMultiEvent[str | re.Pattern, [], str | PlainReturns]):
    """ 根据正则触发一组回调 """

    if TYPE_CHECKING:

        def register(self, rule: re.Pattern, callback) -> None:
            ...

        def unregister(self, rule: re.Pattern | None, callback) -> bool:
            ...

        async def _emit_gen(self, rule_arg: str) -> AsyncGenerator[PlainReturns | str, None]:
            ...
    
        async def emit(self, rule_arg: str) -> list[str | PlainReturns]:
            ...

    def __init__(self, name=""):
        super().__init__(name)
        from mqga.lookup.context import context
        self.matched = context.matched

    def _is_accept(self, rule: re.Pattern, rule_arg: str):
        self.matched.regex = result = rule.search(rule_arg)
        return result

class FilterByEvent(RuleMultiEvent[Callable[[], bool], [], str | PlainReturns]):
    """ 触发一组满足过滤函数的回调 """

    if TYPE_CHECKING:

        def register(self, rule: Callable[[], bool], callback) -> None:
            ...

        def unregister(self, rule: Callable[[], bool] | None, callback) -> bool:
            ...

        async def _emit_gen(self, rule_arg: None) -> AsyncGenerator[PlainReturns | str, None]:
            ...
    
        async def emit(self, rule_arg: None) -> list[str | PlainReturns]:
            ...

    def __init__(self, name=""):
        super().__init__(name)
        from mqga.lookup.context import context
        self.matched = context.matched

    def _is_accept(self, rule: Callable[[], bool], rule_arg: None):
        return rule()

    def _emit_coros(self, rule_arg: None):
        for rule, call in self.callbacks:
            if self._is_accept(rule, rule_arg):
                yield asyncio.create_task(call())
            if self.matched.filter_by:
                del self.matched.filter_by
