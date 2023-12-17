
from mqga.lookup.context import context as ctx
from mqga import on_message, group_only
# from mqga.event.on import on_group_message as on_msg
from mqga.q.message import ChannelMessage, GroupMessage
from mqga.log import log

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

with group_only:

    @on_message.filter_by(lambda: ctx.message.content.lower().endswith("wait"))
    def wait():
        bot = ctx.bot
        payload = ctx.payload
        import asyncio
        async def delay(seconds = 3):
            await asyncio.sleep(seconds)
            await bot._api.group.reply_text(str(seconds), payload)
        return delay()

@on_message.full_match(r"501")
def res501():
    log.error("version:0.0.2\n/ping baidu.com -c 3\n/apikey xxx\n/apiping www.baidu.com -c 3")
    return "version:0.0.2\n/ping baidu.com -c 3\n/apikey xxx\n/apiping www.baidu.com -c 3"
    # 神秘内容，让官方接口返回 Http 501，而不是 json 格式的错误信息
