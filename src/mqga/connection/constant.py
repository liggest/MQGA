from enum import Enum, IntEnum, IntFlag, auto

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

DefaultIntents = Intents.GUILDS | Intents.PUBLIC_GUILD_MESSAGES | Intents.GUILD_MEMBERS

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
#         """ 用户对频道消息附上表情表态 """
#         MessageReactionRemove = "MESSAGE_REACTION_REMOVE"
#         """ 用户对频道消息取消表情表态 """
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
    """ 用户对频道消息附上表情表态 """
    ChannelMessageReactionRemove = "MESSAGE_REACTION_REMOVE"
    """ 用户对频道消息取消表情表态 """
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

class WSState(Enum):
    """ 连接状态 """
    Closed = auto()
    """ 未连接 """
    Connecting = auto()
    """ 正在连接 """
    ConnectedRaw = auto()
    """ 仅已连接 """
    ConnectedSession = auto()
    """ 已链接，已鉴权 """

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
