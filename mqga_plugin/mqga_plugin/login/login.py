from mqga.plugin import plugin_info
from mqga_plugin.game_state_manager import group_game_state_manager, GameState
from mqga_plugin.lan_game_manager import LAN_game_manager

plugin_info(
    name="login",
    author="duolanda",
    version="0.0.1",
    description="输入密码，成功后进入互联网阶段",
)
from mqga import group_context as ctx, on_message
from mqga.q.message import ChannelMessage, GroupMessage
from mqga.log import log

@on_message.regex(r"^\s*/登录\s*(.*)$")
@on_message.regex(r"^\s*/login\s*(.*)$")
async def ping():
    group_state = group_game_state_manager
    message = ctx.message
    if isinstance(message, ChannelMessage):
        id = message.channel_id
    elif isinstance(message, GroupMessage):
        id = message.group_id
    else:
        log.error("我不在群里，也不在频道里，那我在哪？")
    state = group_state.get_group_state(id)

    match = ctx.matched.regex
    info = match.group(1)
    # log.info("让我康康")
    # log.info(info)
    if state is GameState.DISCONNECTED:
        content =   '-&gt;网络数据_疑似获取_开始解析\n' \
                    '⌽⌀⌽�指令:/help\n' \
                    '开始向�␦0x1F66␦⌀�6地址中寻找⌽数据_\n' \
                    '[err␦�⌽⌽or] 0x1F66⌀⌀�6确认⌽␦�到未处理异常…\n' \
                    '写入位置0x0⌽␦␦⌀0000时发生访问�⌽�冲突…\n' \
                    '你���可以忽悠此错�⌽⌽�误并尝␦⌀␦试使用␦/help（/说明书）来���'
        return content
    elif state is GameState.INTERNET or state is GameState.FULLSPEED:
        content = '已经成功登录啦'
        return content
    else:
        game_manager = LAN_game_manager
        if game_manager.can_login(id, info):
            group_state.login_success(id)
            content = '宽带密码输入正确！再输入 /wireless 开启无线网络吧！'
        else:
            content = '密码错误了喔，再好好想想吧'
        return content
