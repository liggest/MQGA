
from mqga.args import args
from mqga.log import log

LEGACY = args.legacy
if LEGACY:
    log.info("【旧 频道模式】…")

RELOAD = args.reload
if not RELOAD:
    def run():
        from mqga.bot import Bot

        bot = Bot()
        bot.run()
else:
    def run():
        import sys
        
        try:
            import watchfiles
        except ImportError:
            log.error("或许当前不是开发环境，watchfiles 未安装，无法热重载")
            sys.exit(1)
        
        from pathlib import Path
        paths = [Path("./src/"), *Path(".").glob("*.py"), *Path(".").glob("*.toml")]
        log.info("正在启用热重载…")
        args = sys.argv
        # if args[0].endswith(".py"):  # 去掉 bot.py 等
        #     args = args[1:]
        cmd = " ".join((sys.executable, *args))
        # TODO 这里接收不到 debug
        # log.debug(f"以下文件变化时执行：{cmd}")
        # log.debug("\n".join(path.as_posix() for path in paths))
        watchfiles.run_process(*paths,
            target=cmd, target_type="command"
        )

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mqga.lookup.context import context, channel_context, group_context

    __all__ = [
        "context", "channel_context", "group_context", 
        "on_message", "on_event", "channel_only", "group_only", "private_only",
        "EventType"
    ]  # 让 ruff 满意

from mqga.lookup.context import __getattr__ as __get_context_attr__

def __getattr__(name: str):
    return __get_context_attr__(name)
    # raise AttributeError

from mqga.event.on import on_message, on_event, channel_only, group_only, private_only
from mqga.q.constant import EventType
