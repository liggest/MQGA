
from mqga import on_channel_message as on_msg, group_context as ctx
from mqga.log import log

from mqga.event.on import on_group_message, on_private_message

@on_group_message
@on_private_message
# @on_channel_message
@on_msg
def log_message():
    log.debug(f"收到消息：{ctx.message!r}")

@on_msg.filter_by(lambda: ctx.message.content.lower().endswith("hello"))
def hello():
    return f"全体目光向我看齐，我宣布个事儿！\nMQGA！[{ctx.message.id}]"

@on_msg.regex(r"bye")
def bye():
    return "晚安"

@on_msg.full_match("$")
def dollar():
    return "🉑"

