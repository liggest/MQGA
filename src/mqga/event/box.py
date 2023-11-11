
from typing import Callable, TypeVar, ParamSpec, Generic

import asyncio

ReturnT = TypeVar("ReturnT")
Params = ParamSpec("Params")

# Callback = Callable[P, T]
# Filter = Callable[P, bool]

class Box(Generic[Params, ReturnT]):

    def __init__(self, func: Callable[Params, ReturnT]):
        if isinstance(func, Box):
            func = func.func
        self.func: Callable[Params, ReturnT] = func
        self.is_async = asyncio.iscoroutinefunction(func)

    async def _call(self, *args: Params.args, **kw: Params.kwargs) -> ReturnT:
        if self.is_async:
            return await self.func(*args, **kw)
        return self.func(*args, **kw)

    __call__ = _call
