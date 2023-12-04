
LEGACY = False
RELOAD = False

def _pre_defined():
    global LEGACY, RELOAD
    
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="MQGA Pre-defined")
    parser.add_argument('-L', '--legacy', action='store_true', help='LEGACY')
    parser.add_argument('-R', '--reload', action='store_true', help='开发模式下的热重载')

    args, rest = parser.parse_known_args()
    
    sys.argv = [sys.argv[0], *rest]

    LEGACY = args.legacy
    RELOAD = args.reload
    if LEGACY:
        from mqga.log import log
        log.info("【旧 频道模式】…")

_pre_defined()

if not RELOAD:
    def run():
        from mqga.bot import Bot

        bot = Bot()
        bot.run()
else:
    def run():
        import sys
        from mqga.log import log
        
        try:
            import watchfiles
        except ImportError:
            log.error("或许当前不是开发环境，watchfiles 未安装，无法热重载")
            sys.exit(1)
        
        from pathlib import Path
        paths = [Path("./src/"), *Path(".").glob("*.py"), *Path(".").glob("*.toml")]
        log.info("正在启用热重载…")
        log.debug("\n".join(path.as_posix() for path in paths))
        args = sys.argv
        if args[0].endswith(".py"):  # 去掉 bot.py 等
            args = args[1:]
        watchfiles.run_process(*paths,
            target=" ".join(("pdm", "bot", *args)), target_type="command"
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
