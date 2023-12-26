
from mqga import on_message, context as ctx
from mqga.log import log
from mqga.event.filter import Filters

from mqga.event.dispatcher import MessageDispatcher
from mqga.q.payload import EventPayload
from mqga.bot import Bot

@on_message.filter_by(Filters.command("cmd", ignore_case=True, context=ctx))
def my_command():
    import random
    param = ctx.matched.filter_by[-1]
    log.debug(f"{param = !r}")
    return "".join(random.choices(param, k=len(param) * 2))

def to_id(bot: Bot, payload):
    return bot.api.of(payload)._payload_to_id(payload)

rejected = {}

@on_message.filter_by(Filters.command("休息", context=ctx))
def rest():
    bot = ctx.bot
    this_id: str = to_id(bot, ctx.payload)

    async def reject_this(dispatcher: MessageDispatcher, bot: Bot, payload: EventPayload):
        condition = to_id(bot, payload) != this_id
        if not condition:  # 是被屏蔽的群号
            log.debug(f"在 {this_id} 睡着呢")
            ctx.message = payload.data  # ctx.message 应该还没被赋值，给它赋上
            condition = condition or is_wake_up()  # 检测是否叫醒
            ctx.message = None         # 把 message 重置掉
            del ctx.matched.filter_by  # 把 filter_by 重置掉，避免之后再重置的时候上下文不一致报错
        return condition
    
    bot._em._all_message_dispatcher.acceptors.append(reject_this)
    if dispatcher := bot._em._dispatchers.get(ctx.payload.type):
        dispatcher.acceptors.append(reject_this)
    rejected[this_id] = reject_this

    return f"在 {this_id} 休息了"

is_wake_up = Filters.command("起床", context=ctx)
@on_message.filter_by(is_wake_up)
def launch():
    bot = ctx.bot
    this_id: str = to_id(bot, ctx.payload)

    if not (reject_this := rejected.get(this_id)):
        return "我这还醒着呢！"
    
    bot._em._all_message_dispatcher.acceptors.remove(reject_this)
    if dispatcher := bot._em._dispatchers.get(ctx.payload.type):
        dispatcher.acceptors.remove(reject_this)

    del rejected[this_id]
    return f"醒了醒了，在 {this_id} 开始干活"

