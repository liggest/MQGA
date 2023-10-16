from enum import IntEnum, IntFlag

class OpCode(IntEnum):
    """
        连接维护用 opcode

        Receive 收过来

        Send 发过去
        
        Reply 回复过去
    """
    Dispatch = 0
    """ Receive 服务端进行消息推送 """
    Heartbeat = 1
    """ Send/Receive 客户端或服务端发送心跳 """
    Identify = 2
    """ Send 客户端发送鉴权 """
    Resume = 6
    """ Send 客户端恢复连接 """
    Reconnect = 7
    """ Receive	服务端通知客户端重新连接 """
    InvalidSession = 9
    """ Receive	当 Identify 或 Resume 的时候，如果参数有错，服务端会返回该消息 """
    Hello = 10
    """ Receive	当客户端与网关建立 ws 连接之后，网关下发的第一条消息 """
    HeartbeatACK = 11
    """ Receive/Reply 当发送心跳成功之后，就会收到该消息 """
    HTTPCallbackACK = 12
    """ Reply 仅用于 http 回调模式的回包，代表机器人收到了平台推送的数据 """

class Intents(IntFlag):
    """ 用于标记一类事件 """
    GUILDS = 1 << 0
    """ 频道 """
    GUILD_MEMBERS = 1 << 1
    """ 频道成员 """
    GUILD_MESSAGES = 1 << 9
    """ 频道消息（私域） """
    GUILD_MESSAGE_REACTIONS = 1 << 10
    """ 频道对消息做表情反馈 """
    DIRECT_MESSAGE = 1 << 12
    """ 私信消息 """
    OPEN_FORUMS_EVENT = 1 << 18
    """ 论坛事件（公域） """
    AUDIO_OR_LIVE_CHANNEL_MEMBER = 1 << 19
    """ 音视频 / 直播子频道成员 """
    INTERACTION  = 1 << 26
    """ 互动事件 """
    MESSAGE_AUDIT = 1 << 27
    """ 消息审核 """
    FORUMS_EVENT = 1 << 28
    """ 论坛事件（私域） """
    AUDIO_ACTION = 1 << 29
    """ 音频动作 """
    PUBLIC_GUILD_MESSAGES = 1 << 30
    """ 频道消息（公域） """

class MsgType(IntEnum):
    Text = 0
    """ 文本 """
    TextImage = 1
    """ 图文混排 """
    Markdown = 2
    Ark = 3
    Embed = 4
    AT = 5

class FileType(IntEnum):
    图片 = 1 
    视频 = 2
    语音 = 3 
    文件 = 4

