""" 开启无线网，进入互联网阶段 """

from mqga_plugin.router_puzzle.game_state_manager import group_game_state_manager, GameState

from mqga import group_context as ctx, on_message
from mqga.q.message import ChannelMessage, GroupMessage
from mqga.log import log

@on_message.full_match(r"/无线")
@on_message.full_match(r"/wireless")
async def wireless():
    group_state = group_game_state_manager

    message = ctx.message
    if isinstance(message, ChannelMessage):
        id = message.channel_id
    elif isinstance(message, GroupMessage):
        id = message.group_id
    else:
        log.error("我不在群里，也不在频道里，那我在哪？")

    state = group_state.get_group_state(id)

    if state is GameState.DISCONNECTED:
        content =   '-&gt;网络数据_疑似获取_开始解析\n' \
                    '⌽⌀⌽�指令:/help\n' \
                    '开始向�␦0x1F66␦⌀�6地址中寻找⌽数据_\n' \
                    '[err␦�⌽⌽or] 0x1F66⌀⌀�6确认⌽␦�到未处理异常…\n' \
                    '写入位置0x0⌽␦␦⌀0000时发生访问�⌽�冲突…\n' \
                    '你���可以忽悠此错�⌽⌽�误并尝␦⌀␦试使用␦/help（/说明书）来���'
        return content
    elif state is GameState.INTERNET or state is GameState.FULLSPEED:
        content = '无线网已经开启了'
        return content
    else:
        if group_game_state_manager.get_login_state(id) is False:
            content = '宽带密码都还没输呢，先去破译破译密码无线网才有用'
        else:
            content = '无线已开启，畅享互联网吧！'
            group_game_state_manager.update_state(id, GameState.INTERNET)
        return content
