from mqga import channel_context as ctx, on_event
from mqga.q.constant import EventType
from mqga.q.message import MessageReaction
from mqga.log import log

@on_event
def log_event():
    log.debug(f"收到事件：{ctx.payload.type}")

# TODO 改进写法
@on_event.of(EventType.ChannelMessageReactionAdd)
async def add_reaction():
    bot = ctx.bot
    data: MessageReaction = ctx.payload.data
    if bot.user and bot.user.id != data.user_id:
        log.debug(f"收到表情表态：{data!r}")
        if all(bot.user.id != user.id for user in 
                await bot._api.channel_reaction_get_head_users(data, data.emoji)):
            log.debug("自己也贴个表情…")
            return data.emoji
    else:
        log.debug(f"收到自己的表情表态：{data!r}")

# TODO 改进写法
@on_event.of(EventType.ChannelMessageReactionRemove)
async def remove_reaction():
    bot = ctx.bot
    data: MessageReaction = ctx.payload.data
    if bot.user and bot.user.id != data.user_id:
        log.debug(f"表情表态被取消：{data!r}")
        if any(bot.user.id == user.id for user in 
                await bot._api.channel_reaction_get_head_users(data, data.emoji)):
            log.debug("也取消自己贴的表情…")
            await bot._api.channel_reaction_delete(data, data.emoji)
    else:
        log.debug(f"自己的表情表态被取消：{data!r}")
