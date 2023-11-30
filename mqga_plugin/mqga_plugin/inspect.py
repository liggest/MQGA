
from mqga.lookup.context import context as ctx
from mqga import on_message, group_only
# from mqga.event.on import on_group_message as on_msg
from mqga.q.message import ChannelMessage, GroupMessage

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
            await bot._api.group_reply(str(seconds), payload)
        return delay()
