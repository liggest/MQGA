from mqga.plugin import plugin_info
from mqga_plugin.game_state_manager import group_game_state_manager, GameState

plugin_info(
    name="game_helpback",
    author="duolanda",
    version="0.0.1",
    description="隐藏的路由器背面"
)
from mqga import group_context as ctx, on_message
from mqga.q.message import ChannelMessage, GroupMessage
from mqga.log import log

@on_message.full_match(r"/helpback")
async def game_helpback():
    group_state = group_game_state_manager

    message = ctx.message
    if isinstance(message, ChannelMessage):
        id = message.channel_id
    elif isinstance(message, GroupMessage):
        id = message.group_id
    else:
        log.error(f"我不在群里，也不在频道里，那我在哪？")

    state = group_state.get_group_state(id)
    # log.info("我看看怎么个事")
    # log.info(state)
   
    if state is GameState.INTERNET or state is GameState.FULLSPEED:
        content = '天呐，这都被你发现了！如果想要获得高速稳定的网络，你还需要开启 5Ghz！' 
    else:
        content = '这里有内容！但是需要联网后才能查看' 
    return content