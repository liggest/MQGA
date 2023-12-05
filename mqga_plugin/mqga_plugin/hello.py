
from mqga import group_context as ctx, on_message, channel_only, group_only
from mqga import on_event, EventType
from mqga.log import log

# from mqga.event.on import on_group_message, on_message, on_channel_message

@on_event.of(EventType.WSReady)
def ready():
    log.info(f"{ctx.bot.user} 机器人已就绪")

# @on_group_message
# @on_private_message
# @on_channel_message
@on_message
def log_message():
    log.debug(f"收到消息：{ctx.message!r}")

with channel_only:

    with group_only:

        @on_message.filter_by(lambda: ctx.message.content.lower().endswith("hello"))
        def hello():
            return f"全体目光向我看齐，我宣布个事儿！\nMQGA！[{ctx.message.id.replace('.', '[.]')}]"

    @on_message.regex(r"bye")
    def bye():
        return "晚安"

with group_only:

    @on_message.full_match("$")
    def dollar():
        return "🉑"


    @on_message.filter_by(lambda: ctx.message.content.strip().lower().startswith("/img"))
    async def img():
        url = ctx.message.content.strip().lower().removeprefix("/img")
        file = await ctx.bot._api.group.file(ctx.message.group_id, url)
        log.debug(f"FileInfo: {file!r}")
        await ctx.bot._api.group.reply_media(f"FileInfo: {file!r}", file, ctx.payload)

from mqga.plugin import plugin_info

plugin_info(
    name="你好",
    author="哆啦NDA",
    version="0.0.1",
    description="测试插件"
)
