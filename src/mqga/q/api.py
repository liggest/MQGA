from typing import TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import NotRequired

    class SessionStartLimit(TypedDict):
        """ 当前的 session 启动限制 """
        total: int
        """ 每 24 小时可创建 Session 数 """
        remaining: int
        """ 目前还可以创建的 Session 数 """
        reset_after: int
        """ 重置计数的剩余时间（毫秒） """
        max_concurrency: int
        """ 每 5 秒可以创建的 Session 数 """

    class WSURL(TypedDict):
        url: str
        """ ws 连接地址 """
        shards: NotRequired[int]
        """ 建议的 shard 数 """
        session_start_limit: NotRequired[SessionStartLimit]

    class AccessToken(TypedDict):
        access_token: str
        expires_in: str

    class RepliedMessage(TypedDict):
        id: str
        """ 消息 id """
        timestamp: int

    class FileInfo(TypedDict):
        file_uuid: str
        """ 文件 id """
        file_info: str
        """ 文件信息 """
        ttl: int
        """ 有效期，为 0 时一直有效 """
