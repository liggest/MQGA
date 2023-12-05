
from mqga.plugin import plugin_info

plugin_info(
    name="pingbot",
    author="liuyu",
    version="0.0.1",
    description="你就说ping没ping吧"
)
from mqga import group_context as ctx, on_message

@on_message.regex(r"^\s*/ping\s*(.+)$")
def ping():
    info = ctx.message.content.replace("/ping","").strip()
    botname = ctx.bot.user.username
    return f"ping到{botname}了,但是{info}没反应咧"

