

import httpx

from mqga.lookup.context import context as ctx
from mqga.event.on import on_message
from mqga.q.message import ChannelMessage, GroupMessage

from mqga.q.constant import FileType
from mqga.lookup.context import BotContext
from mqga_plugin.toolz.filter import Filters


@on_message.filter_by(lambda: ctx.message.content.lower().endswith("test"))
def test():
    message = ctx.message
    source_info = ""
    if isinstance(message, ChannelMessage):
        source_info = f"{message.channel_id = }\n"
    elif isinstance(message, GroupMessage):
        source_info = f"{message.group_id = }\n"
    return f"""{message.id = }
{source_info}{message.author = }
{message.content = !r}
{message.attachments = !r}""".replace(".", "[.]")


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

