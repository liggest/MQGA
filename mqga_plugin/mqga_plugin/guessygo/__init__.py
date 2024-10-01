
from mqga.plugin import plugin_info

plugin_info("游戏王猜卡游戏", description="\n- 更新卡包\n- /猜卡游戏\n- 我猜xxx\n- 提示\n- 取消")

from mqga_plugin.guessygo import dl,guess

__all__ = ["dl", "guess"]
