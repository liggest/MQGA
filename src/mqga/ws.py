

class Payload:  # TODO 重要：决定这是一个什么东西（纯 dict？ dict 子类？ MutableMapping 子类？ dataclass？ BaseModel？ TypedDict?）
    pass

class WS:

    def __init__(self, bot):
        raise NotImplementedError   # TODO

    async def init(self):
        # TODO GET /gateway
        raise NotImplementedError
