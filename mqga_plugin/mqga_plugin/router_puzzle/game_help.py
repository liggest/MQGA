""" 返回路由器说明书 """

from mqga_plugin.router_puzzle.game_state_manager import group_game_state_manager, GameState

from mqga import group_context as ctx, on_message
from mqga.q.message import ChannelMessage, GroupMessage
from mqga.log import log

@on_message.full_match(r"/说明书")
@on_message.full_match(r"/help")
async def game_help():
    group_state = group_game_state_manager

    message = ctx.message
    if isinstance(message, ChannelMessage):
        id = message.channel_id
    elif isinstance(message, GroupMessage):
        id = message.group_id
    else:
        log.error("我不在群里，也不在频道里，那我在哪？")

    state = group_state.get_group_state(id)
    # log.info("我看看怎么个事")
    # log.info(state)
    if state is GameState.DISCONNECTED:
        content =   '这里?路由?说明书:\n' \
                    '/help（/说明书）：查看?明，帮助?由器联?\n' \
                    '/state（/状态）：查看路?器运?状?\n' \
                    '/p???（/插??）：接????线???\n' \
                    '如果你想要?接到?联网，需要?插??线，???????，并????????'
        return content
    elif state is GameState.LAN:
        content =   '这里?路由?说明书:\n' \
                    '/help（/说明书）：查看?明，帮助?由器联?\n' \
                    '/state（/状态）：查看路?器运?状?\n' \
                    '/plug（/插网线）：接?计?机和路??网线\n' \
                    '/s??n（/扫?）：扫?这??算机在局域?可??问的 ip\n' \
                    '/pi??（/?测）：访问???址\n' \
                    '/lo??n（/登?）：通过输??取的宽?密?连接??络\n' \
                    '/wir?le??（/无?）：开启无??，畅??络\n' \
                    '如果你想要?接到?联网，需要?插??线，设??带的?号，并????????'
        return content
    elif state is GameState.INTERNET or state is GameState.FULLSPEED:
        content =   '这里是路由器说明书:\n' \
        '/help（/说明书）：查看说明，帮助路由器联网\n' \
        '/state（/状态）：查看路由器运行状态\n' \
        '/plug（/插网线）：接入计算机和路由器网线\n' \
        '/scan（/扫描）：扫描这台计算机在局域网可以访问的 ip\n' \
        '/ping（/探测）：访问不同地址\n' \
        '/login（/登录）：通过输入获取的宽带密码连接到网络\n' \
        '/wireless（/无线）：开启无线网，畅游网络\n' \
        '如果你想要连接到互联网，需要先插入网线，设置宽带的账号，并正确配置无线网部分。'
        return content
    else:
        return "你来到了荒漠"
