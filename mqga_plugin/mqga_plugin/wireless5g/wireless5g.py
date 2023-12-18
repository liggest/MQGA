from mqga.plugin import plugin_info
from mqga_plugin.game_state_manager import group_game_state_manager, GameState

plugin_info(
    name="wireless5g",
    author="duolanda",
    version="0.0.1",
    description="开启 5G，全速运行"
)
from mqga import group_context as ctx, on_message
from mqga.q.message import ChannelMessage, GroupMessage
from mqga.log import log

@on_message.full_match(r"/wireless_5g")
async def wireless5g():
    group_state = group_game_state_manager

    message = ctx.message
    if isinstance(message, ChannelMessage):
        id = message.channel_id
    elif isinstance(message, GroupMessage):
        id = message.group_id
    else:
        log.error(f"我不在群里，也不在频道里，那我在哪？")

    state = group_state.get_group_state(id)

    if state is GameState.INTERNET:
        content = '原来角落中还有这个选项？！5Ghz，启动！'
        group_game_state_manager.update_state(id,GameState.FULLSPEED)
    else:
        content = '那个……现在还没有连到互联网呢'
    return content
  