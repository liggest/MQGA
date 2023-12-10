
from typing import TypeVar, Generic
from contextvars import ContextVar

T = TypeVar("T")

class VarProperty(Generic[T]):

    def __init__(self, var: ContextVar[T], default=None):
        self.var = var
        self.default = default
        self._token = None

    def __get__(self, obj, cls) -> T:
        return self.var.get()

    def __set__(self, obj, val: T):
        if self._token is None:
            self._token = self.var.set(val)
        else:
            self.var.set(val)
    
    def __delete__(self, obj):
        if self._token:
            self.var.reset(self._token)
            self._token = None
        else:
            self.__set__(obj, self.default)
