from enum import Enum, IntEnum, IntFlag
from dataclasses import dataclass

class OpCode(IntEnum):
    """
        操作码，用来维护连接

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
    """ 用于标记一类事件，表明 ws 接收该类事件的意向 """
    NONE = 0
    """ 无 """
    
    GUILDS = 1 << 0
    """ 频道 """
    GUILD_MEMBERS = 1 << 1
    """ 频道成员 """
    GUILD_MESSAGES = 1 << 9
    """ 频道消息（私域） """
    GUILD_MESSAGE_REACTIONS = 1 << 10
    """ 频道消息被贴表情 """
    DIRECT_MESSAGE = 1 << 12
    """ 私信消息 """
    OPEN_FORUMS_EVENT = 1 << 18
    """ 论坛事件（公域） """
    AUDIO_OR_LIVE_CHANNEL_MEMBER = 1 << 19
    """ 音视频 / 直播子频道成员 """
    GROUP_PRIVATE_MESSAGES = 1 << 25  # 暂定
    """ 群、私聊消息 """
    INTERACTION  = 1 << 26
    """ 消息按钮交互事件 """
    MESSAGE_AUDIT = 1 << 27
    """ 消息审核 """
    FORUMS_EVENT = 1 << 28
    """ 论坛事件（私域） """
    AUDIO_ACTION = 1 << 29
    """ 音频动作 """
    PUBLIC_GUILD_MESSAGES = 1 << 30
    """ 频道消息（公域） """
    
    DEFAULT = GUILDS | PUBLIC_GUILD_MESSAGES | GUILD_MEMBERS
    """ 默认意向 """

# DefaultIntents = Intents.GUILDS | Intents.PUBLIC_GUILD_MESSAGES | Intents.GUILD_MEMBERS

# class Event:
#     """ 事件 """
#     class WS(str, Enum):
#         """ ws 事件 """
#         Ready = "READY"
#         """ 连接准备完成 """
#         Resumed = "RESUMED"
#         """ 连接恢复 """
    
#     class Group(str, Enum):
#         """ 群事件 """
#         AtMessageCreate = "GROUP_AT_MESSAGE_CREATE"
#         """ 群内 @ 消息 """
#         Join = "GROUP_ADD_ROBOT"
#         """ 被加入群 """
#         Delete = "GROUP_DEL_ROBOT"
#         """ 被移出群 """
#         MessageDisable = "GROUP_MSG_REJECT"
#         """ 关闭消息通知 """
#         MessageEnable = "GROUP_MSG_RECEIVE"
#         """ 开启消息通知 """
#         # 未开放：
#         # 用户加入群聊
#         # 用户退出群聊

#     class Private(str, Enum):
#         """ 私聊事件 """
#         MessageCreate = "C2C_MESSAGE_CREATE"
#         """ 私聊消息 """
#         FriendAdd = "FRIEND_ADD"
#         """ 被添加好友 """
#         FirendDelete = "FRIEND_DEL"
#         """ 被删除好友 """
#         MessageDisable = "C2C_MSG_REJECT"
#         """ 关闭消息通知 """
#         MessageEnable = "C2C_MSG_REJECT"
#         """ 开启消息通知 """

#     class Guild(str, Enum):
#         """ 频道公域事件 """
#         Join = "GUILD_CREATE"
#         """ 被加入频道 """
#         Update = "GUILD_UPDATE"
#         """ 频道信息变化 """
#         Delete = "GUILD_DELETE"
#         """ 被移出频道 """
#         MemberAdd = "GUILD_MEMBER_ADD"
#         """ 用户加入频道 """
#         MemberUpdate = "GUILD_MEMBER_UPDATE"
#         """ 频道用户信息变化 """
#         MemberRemove = "GUILD_MEMBER_REMOVE"
#         """ 用户离开频道 """

#     class Channel(str, Enum):
#         """ 子频道事件 """
#         AtMessageCreate = "AT_MESSAGE_CREATE"
#         """ 频道 @ 消息 """
#         MessageCreate = "MESSAGE_CREATE"
#         """ 频道消息 """
#         MessageReactionAdd = "MESSAGE_REACTION_ADD"
#         """ 用户对频道消息贴表情 """
#         MessageReactionRemove = "MESSAGE_REACTION_REMOVE"
#         """ 用户对频道消息揭表情 """
#         MessageAuditPass = "MESSAGE_AUDIT_PASS"
#         """ 消息审核通过 """
#         MessageAuditReject = "MESSAGE_AUDIT_REJECT"
#         """ 消息审核否决 """
#         InteractionCreate = "INTERACTION_CREATE"
#         """ 用户点击消息中的按钮 """
#         Create = "CHANNEL_CREATE"
#         """ 子频道被创建 """
#         Update = "CHANNEL_UPDATE"
#         """ 子频道信息变化 """
#         Delete = "CHANNEL_DELETE"
#         """ 子频道被删除 """
#         AudioOrLiveMemberEnter = "AUDIO_OR_LIVE_CHANNEL_MEMBER_ENTER"
#         """ 用户进入音视频、直播子频道 """
#         AudioOrLiveMemberExit = "AUDIO_OR_LIVE_CHANNEL_MEMBER_ENTER"
#         """ 用户退出音视频、直播子频道 """

#     class Direct(str, Enum):
#         """ 频道私信事件 """
#         MessageCreate = "DIRECT_MESSAGE_CREATE"
#         """ 频道私信消息 """

#     class Forum(str, Enum):
#         """ 话题子频道事件 """
#         ThreadCreate = "FORUM_THREAD_CREATE"
#         """ 主题帖被创建 """
#         ThreadUpdate = "FORUM_THREAD_UPDATE"
#         """ 主题帖信息变化 """
#         ThreadDelete = "FORUM_THREAD_DELETE"
#         """ 主题帖被删除 """
#         PostCreate = "FORUM_POST_CREATE"
#         """ 帖子被创建 """
#         PostDelete = "FORUM_POST_DELETE"
#         """ 帖子被删除 """
#         ReplyCreate = "FORUM_REPLY_CREATE"
#         """ 回复被创建 """
#         ReplyDelete = "FORUM_REPLY_DELETE"
#         """ 回复被删除 """
#         AuditResult = "FORUM_PUBLISH_AUDIT_RESULT"
#         """ 帖子审核结果 """
    
#     class OpenForum(str, Enum):
#         """ 话题子频道事件 """
#         ThreadCreate = "OPEN_FORUM_THREAD_CREATE"
#         """ 主题帖被创建 """
#         ThreadUpdate = "OPEN_FORUM_THREAD_UPDATE"
#         """ 主题帖信息变化 """
#         ThreadDelete = "OPEN_FORUM_THREAD_DELETE"
#         """ 主题帖被删除 """
#         PostCreate = "OPEN_FORUM_POST_CREATE"
#         """ 帖子被创建 """
#         PostDelete = "OPEN_FORUM_POST_DELETE"
#         """ 帖子被删除 """
#         ReplyCreate = "OPEN_FORUM_REPLY_CREATE"
#         """ 回复被创建 """
#         ReplyDelete = "OPEN_FORUM_REPLY_DELETE"
#         """ 回复被删除 """
    
#     class Audio(str, Enum):
#         """ 音频事件 """
#         Start = "AUDIO_START"
#         """ 播放开始 """
#         Finish = "AUDIO_FINISH"
#         """ 播放结束 """
#         OnMic = "AUDIO_ON_MIC"
#         """ 上麦时 """
#         OffMic = "AUDIO_OFF_MIC"
#         """ 下麦时 """

class EventType(str, Enum):
    """ 事件类型 """
    
    # WS
    WSReady = "READY"
    """ ws 连接准备完成 """
    WSResumed = "RESUMED"
    """ ws 连接恢复 """

    # 群
    GroupAtMessageCreate = "GROUP_AT_MESSAGE_CREATE"
    """ 群内 @ 消息 """
    GroupJoin = "GROUP_ADD_ROBOT"
    """ 被加入群 """
    GroupDelete = "GROUP_DEL_ROBOT"
    """ 被移出群 """
    GroupMessageDisable = "GROUP_MSG_REJECT"
    """ 关闭群消息通知 """
    GroupMessageEnable = "GROUP_MSG_RECEIVE"
    """ 开启群消息通知 """
    # 未开放：
    # 用户加入群聊
    # 用户退出群聊


    # 私聊
    PrivateMessageCreate = "C2C_MESSAGE_CREATE"
    """ 私聊消息 """
    PrivateFriendAdd = "FRIEND_ADD"
    """ 被添加好友 """
    PrivateFirendDelete = "FRIEND_DEL"
    """ 被删除好友 """
    PrivateMessageDisable = "C2C_MSG_REJECT"
    """ 关闭私聊消息通知 """
    PrivateMessageEnable = "C2C_MSG_REJECT"
    """ 开启私聊消息通知 """


    # 频道公域
    GulidJoin = "GUILD_CREATE"
    """ 被加入频道 """
    GulidUpdate = "GUILD_UPDATE"
    """ 频道信息变化 """
    GulidDelete = "GUILD_DELETE"
    """ 被移出频道 """
    GulidMemberAdd = "GUILD_MEMBER_ADD"
    """ 用户加入频道 """
    GulidMemberUpdate = "GUILD_MEMBER_UPDATE"
    """ 频道用户信息变化 """
    GulidMemberRemove = "GUILD_MEMBER_REMOVE"
    """ 用户离开频道 """
    GulidMessageDelete = "PUBLIC_MESSAGE_DELETE"
    """ 公域消息被撤回 """

    # 消息子频道
    ChannelAtMessageCreate = "AT_MESSAGE_CREATE"
    """ 频道 @ 消息 """
    ChannelMessageCreate = "MESSAGE_CREATE"
    """ 频道消息 """
    ChannelMessageDelete = "MESSAGE_DELETE"
    """ 频道消息撤回 """
    ChannelMessageReactionAdd = "MESSAGE_REACTION_ADD"
    """ 在频道消息上贴表情 """
    ChannelMessageReactionRemove = "MESSAGE_REACTION_REMOVE"
    """ 在频道消息上揭表情 """
    ChannelMessageAuditPass = "MESSAGE_AUDIT_PASS"
    """ 消息审核通过 """
    ChannelMessageAuditReject = "MESSAGE_AUDIT_REJECT"
    """ 消息审核否决 """
    ChannelInteractionCreate = "INTERACTION_CREATE"
    """ 用户点击消息中的按钮 """
    ChannelCreate = "CHANNEL_CREATE"
    """ 子频道被创建 """
    ChannelUpdate = "CHANNEL_UPDATE"
    """ 子频道信息变化 """
    ChannelDelete = "CHANNEL_DELETE"
    """ 子频道被删除 """

    # 音视频、直播子频道
    AudioOrLiveMemberEnter = "AUDIO_OR_LIVE_CHANNEL_MEMBER_ENTER"
    """ 用户进入音视频、直播子频道 """
    AudioOrLiveMemberExit = "AUDIO_OR_LIVE_CHANNEL_MEMBER_ENTER"
    """ 用户退出音视频、直播子频道 """

    # 频道私信
    DirectMessageCreate = "DIRECT_MESSAGE_CREATE"
    """ 频道私信消息 """
    DirectMessageDelete = "DIRECT_MESSAGE_DELETE"
    """ 频道私信消息被撤回 """

    # 话题子频道
    ForumThreadCreate = "FORUM_THREAD_CREATE"
    """ 话题子频道中主题帖被创建 """
    ForumThreadUpdate = "FORUM_THREAD_UPDATE"
    """ 话题子频道中主题帖信息变化 """
    ForumThreadDelete = "FORUM_THREAD_DELETE"
    """ 话题子频道中主题帖被删除 """
    ForumPostCreate = "FORUM_POST_CREATE"
    """ 话题子频道中帖子被创建 """
    ForumPostDelete = "FORUM_POST_DELETE"
    """ 话题子频道中帖子被删除 """
    ForumReplyCreate = "FORUM_REPLY_CREATE"
    """ 话题子频道中回复被创建 """
    ForumReplyDelete = "FORUM_REPLY_DELETE"
    """ 话题子频道中回复被删除 """
    ForumAuditResult = "FORUM_PUBLISH_AUDIT_RESULT"
    """ 话题子频道中帖子审核结果 """

    # 公域帖子
    OpenForumThreadCreate = "OPEN_FORUM_THREAD_CREATE"
    """ 公域论坛中主题帖被创建 """
    OpenForumThreadUpdate = "OPEN_FORUM_THREAD_UPDATE"
    """ 公域论坛中主题帖信息变化 """
    OpenForumThreadDelete = "OPEN_FORUM_THREAD_DELETE"
    """ 公域论坛中主题帖被删除 """
    OpenForumPostCreate = "OPEN_FORUM_POST_CREATE"
    """ 公域论坛中帖子被创建 """
    OpenForumPostDelete = "OPEN_FORUM_POST_DELETE"
    """ 公域论坛中帖子被删除 """
    OpenForumReplyCreate = "OPEN_FORUM_REPLY_CREATE"
    """ 公域论坛中回复被创建 """
    OpenForumReplyDelete = "OPEN_FORUM_REPLY_DELETE"
    """ 公域论坛中回复被删除 """

    # 音频子频道
    AudioStart = "AUDIO_START"
    """ 音频子频道播放开始 """
    AudioFinish = "AUDIO_FINISH"
    """ 音频子频道播放结束 """
    AudioOnMic = "AUDIO_ON_MIC"
    """ 音频子频道上麦时 """
    AudioOffMic = "AUDIO_OFF_MIC"
    """ 音频子频道下麦时 """

@dataclass(frozen=True)
class EventPair:
    intent: Intents
    """ 事件接收意向 """
    type: EventType
    """ 事件类型 """
    is_private: bool = False
    """ 是私域事件 """

class EventType2Intent(EventPair, Enum):
    """ 事件类型与接收意向的对应关系 """

    READY   = (Intents.NONE, EventType.WSReady)
    RESUMED = (Intents.NONE, EventType.WSResumed)

    GUILD_CREATE   = (Intents.GUILDS, EventType.GulidJoin)
    GUILD_DELETE   = (Intents.GUILDS, EventType.GulidDelete)
    GUILD_UPDATE   = (Intents.GUILDS, EventType.GulidUpdate)
    CHANNEL_CREATE = (Intents.GUILDS, EventType.ChannelCreate)
    CHANNEL_UPDATE = (Intents.GUILDS, EventType.ChannelUpdate)
    CHANNEL_DELETE = (Intents.GUILDS, EventType.ChannelDelete)
    
    GUILD_MEMBER_ADD    = (Intents.GUILD_MEMBERS, EventType.GulidMemberAdd)
    GUILD_MEMBER_UPDATE = (Intents.GUILD_MEMBERS, EventType.GulidMemberUpdate)
    GUILD_MEMBER_REMOVE = (Intents.GUILD_MEMBERS, EventType.GulidMemberRemove)

    MESSAGE_CREATE = (Intents.GUILD_MESSAGES, EventType.ChannelMessageCreate, True)  # 私域
    MESSAGE_DELETE = (Intents.GUILD_MESSAGES, EventType.ChannelMessageDelete, True)

    MESSAGE_REACTION_ADD    = (Intents.GUILD_MESSAGE_REACTIONS, EventType.ChannelMessageReactionAdd)
    MESSAGE_REACTION_REMOVE = (Intents.GUILD_MESSAGE_REACTIONS, EventType.ChannelMessageReactionRemove)

    DIRECT_MESSAGE_CREATE = (Intents.DIRECT_MESSAGE, EventType.DirectMessageCreate)
    DIRECT_MESSAGE_DELETE = (Intents.DIRECT_MESSAGE, EventType.DirectMessageDelete)

    OPEN_FORUM_THREAD_CREATE = (Intents.OPEN_FORUMS_EVENT, EventType.OpenForumThreadCreate)
    OPEN_FORUM_THREAD_UPDATE = (Intents.OPEN_FORUMS_EVENT, EventType.OpenForumThreadUpdate)
    OPEN_FORUM_THREAD_DELETE = (Intents.OPEN_FORUMS_EVENT, EventType.OpenForumThreadDelete)
    OPEN_FORUM_POST_CREATE   = (Intents.OPEN_FORUMS_EVENT, EventType.OpenForumPostCreate)
    OPEN_FORUM_POST_DELETE   = (Intents.OPEN_FORUMS_EVENT, EventType.OpenForumPostDelete)
    OPEN_FORUM_REPLY_CREATE  = (Intents.OPEN_FORUMS_EVENT, EventType.OpenForumReplyCreate)
    OPEN_FORUM_REPLY_DELETE  = (Intents.OPEN_FORUMS_EVENT, EventType.OpenForumReplyDelete)

    AUDIO_OR_LIVE_CHANNEL_MEMBER_ENTER = (Intents.AUDIO_OR_LIVE_CHANNEL_MEMBER, EventType.AudioOrLiveMemberEnter)
    AUDIO_OR_LIVE_CHANNEL_MEMBER_EXIT  = (Intents.AUDIO_OR_LIVE_CHANNEL_MEMBER, EventType.AudioOrLiveMemberExit)

    INTERACTION_CREATE = (Intents.INTERACTION, EventType.ChannelInteractionCreate)

    MESSAGE_AUDIT_PASS   = (Intents.MESSAGE_AUDIT, EventType.ChannelMessageAuditPass)
    MESSAGE_AUDIT_REJECT = (Intents.MESSAGE_AUDIT, EventType.ChannelMessageAuditReject)

    FORUM_THREAD_CREATE = (Intents.FORUMS_EVENT, EventType.ForumThreadCreate, True)  # 私域
    FORUM_THREAD_UPDATE = (Intents.FORUMS_EVENT, EventType.ForumThreadUpdate, True)
    FORUM_THREAD_DELETE = (Intents.FORUMS_EVENT, EventType.ForumThreadDelete, True)
    FORUM_POST_CREATE   = (Intents.FORUMS_EVENT, EventType.ForumPostCreate, True)
    FORUM_POST_DELETE   = (Intents.FORUMS_EVENT, EventType.ForumPostDelete, True)
    FORUM_REPLY_CREATE  = (Intents.FORUMS_EVENT, EventType.ForumReplyCreate, True)
    FORUM_REPLY_DELETE  = (Intents.FORUMS_EVENT, EventType.ForumReplyDelete, True)
    FORUM_PUBLISH_AUDIT_RESULT = (Intents.FORUMS_EVENT, EventType.ForumAuditResult, True)

    AUDIO_START   = (Intents.AUDIO_ACTION, EventType.AudioStart)
    AUDIO_FINISH  = (Intents.AUDIO_ACTION, EventType.AudioFinish)
    AUDIO_ON_MIC  = (Intents.AUDIO_ACTION, EventType.AudioOnMic)
    AUDIO_OFF_MIC = (Intents.AUDIO_ACTION, EventType.AudioOffMic)

    AT_MESSAGE_CREATE = (Intents.PUBLIC_GUILD_MESSAGES, EventType.ChannelAtMessageCreate)
    PUBLIC_MESSAGE_DELETE = (Intents.PUBLIC_GUILD_MESSAGES, EventType.GulidMessageDelete)

    # TODO 群和私聊
    C2C_MESSAGE_CREATE = (Intents.GROUP_PRIVATE_MESSAGES, EventType.PrivateMessageCreate)
    GROUP_AT_MESSAGE_CREATE = (Intents.GROUP_PRIVATE_MESSAGES, EventType.GroupAtMessageCreate)

class RoleID(str, Enum):
    """ 身份组 ID """
    All = "1"
    """ 全体成员 """
    Admin = "2"
    """ 管理员 """
    Owner = "4"
    """ 群主 / 创建者 """
    ChannelAdmin = "5"
    """ 子频道管理员 """

class ReactionTargetType(IntEnum):
    """ 表态对象类型 """
    Message = 0
    """ 对消息 """
    Thread = 1     # 名称暂定
    """ 对帖子 """
    Post = 2       # 名称暂定
    """ 对评论？ """
    Reply = 3
    """ 对回复 """

class EmojiType(IntEnum):
    """ 表情类型 """
    System = 1
    """ QQ 表情 """
    Emoji = 2
    """ 真正的 emoji """

class MessageType(IntEnum):
    """ 消息类型 """
    Text = 0
    """ 文本 """
    TextImage = 1
    """ 图文混排 """
    Markdown = 2
    Ark = 3
    Embed = 4
    AT = 5
    Media = 7
    """ 富媒体 """

class FileType(IntEnum):
    图片 = 1
    """ png / jpg """ 
    视频 = 2
    """ mp4 """
    语音 = 3
    """ silk """ 
    文件 = 4
