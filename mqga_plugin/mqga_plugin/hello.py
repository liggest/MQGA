
from mqga import context as ctx, on_message, channel_only, group_only
from mqga import on_event, EventType
from mqga.log import log

from mqga_plugin.toolz import Filters
from mqga.q.constant import FileType
from mqga.lookup.context import BotContext

import httpx

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
    @on_message.full_match("$")
    @on_message.full_match("$")
    def dollar():
        return "🉑"

async def reply_media_or_timeout(ctx: BotContext, url: str, content: str = "", file_type: FileType = FileType.图片):
    try:
        await ctx.bot.api.reply_media(url, ctx.payload, content=content, file_type=file_type)
    except httpx.ReadTimeout:
        await ctx.bot.api.reply_text("超时啦 > <", ctx.payload)

# @on_message.filter_by(lambda: (ctx.matched << ctx.message.content.strip().lower()).startswith("/img"))
@on_message.filter_by(Filters.command("img", context=ctx))
@on_message.filter_by(Filters.command("image", context=ctx))
async def img():
    # cmd: str = ctx.matched.filter_by[0]
    # url = cmd.removeprefix("/img").lstrip()
    url = ctx.matched.filter_by[-1]
    # file = await ctx.bot.api.group.file(ctx.in_group.message.group_id, url)
    # log.debug(f"FileInfo: {file!r}")
    # return ctx.bot.api.group.reply_media(file, ctx.payload)
    # return ctx.bot.api.reply_media(url, ctx.payload)
    return reply_media_or_timeout(ctx, url)

@on_message.filter_by(Filters.command("audio", context=ctx))
async def audio():
    url = ctx.matched.filter_by[-1]
    return reply_media_or_timeout(ctx, url, file_type=FileType.语音)

@on_message.filter_by(Filters.command("video", context=ctx))
async def video():
    url = ctx.matched.filter_by[-1]
    return reply_media_or_timeout(ctx, url, file_type=FileType.视频)

@on_message.regex(r"[/]?(lr|左右)\s*(?P<left>\S+)?\s*(?P<right>\S+)?")
async def lr():
    match = ctx.matched.regex
    left, right = match.group('left'), match.group('right')
    return f"{left = !r}  {right = !r}"

@on_message.full_match(r"数数")
def count():
    import asyncio
    async def _do_count():
        reply = ctx.bot.api.of(ctx.payload).reply_text
        for i in range(10):
            await reply(str(i), ctx.payload)
            await asyncio.sleep(1)
    return _do_count()

bite_to = None

@on_message.full_match(r"咬住")
def bite():
    global bite_to
    if not bite_to:
        bite_to = ctx.payload
        
    async def _do_bite():
        global bite_to
        from mqga.connection.api.client import APIError
        try:
            await ctx.bot.api.reply_text("汪汪汪", bite_to)
        except APIError:
            bite_to = None
    
    return _do_bite()

from mqga.plugin import plugin_info

plugin_info(
    name="你好",
    author="哆啦NDA",
    version="0.0.1",
    description="测试插件"
)
