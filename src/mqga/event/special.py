
import re
from typing import TYPE_CHECKING, AsyncGenerator

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
    
        async def emit(self, rule_arg: str):
            ...

    def __init__(self, name=""):
        super().__init__(name)
        from mqga.lookup.context import context
        self.context = context

    def _is_accept(self, rule: re.Pattern, rule_arg: str):
        self.context.matched_regex = result = rule.search(rule_arg)
        return result
