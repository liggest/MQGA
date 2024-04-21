
from mqga.plugin import plugin_info

plugin_info(
    name="router_puzzle",
    author="duolanda",
    version="0.0.1",
    description="路由器解谜游戏"
)

from mqga_plugin.router_puzzle import game_help, game_helpback, login, game_ping, plug, scan
from mqga_plugin.router_puzzle import game_state, state_test, wireless, wireless5g

__all__ = ["game_help", "game_helpback", "login", "game_ping", "plug", "scan",
           "game_state", "state_test", "wireless", "wireless5g"]
