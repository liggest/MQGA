
from typing import TypeVar, Generic
from contextvars import ContextVar

T = TypeVar("T")

class VarProperty(Generic[T]):

    def __init__(self, var: ContextVar[T], default=None):
        self.var = var
        self.default = default

    def __get__(self, obj, cls) -> T | None:
        return self.var.get()

    def __set__(self, obj, val: T | None):
        return self.var.set(val)
    
    def __delete__(self, obj):
        self.var.set(self.default)
