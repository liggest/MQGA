
from mqga import group_context as ctx, on_message

@on_message.regex(r"^\s*/ping\s*(.+)$")
def ping():
    info = ctx.message.content.replace("/ping","").strip()
    botname = ctx.bot.user.username
    return f"ping到{botname}了,但是{info}没反应咧"

