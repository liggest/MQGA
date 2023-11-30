
LEGACY = False

def _pre_defined():
    global LEGACY
    
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="MQGA Pre-defined")
    parser.add_argument('-L', '--legacy', action='store_true', help='LEGACY')

    args, rest = parser.parse_known_args()
    
    sys.argv = [sys.argv[0], *rest]

    LEGACY = args.legacy
    if LEGACY:
        print("【旧 频道模式】…")

_pre_defined()

def run():
    from mqga.bot import Bot

    bot = Bot()
    bot.run()

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mqga.lookup.context import context, channel_context, group_context

    __all__ = [
        "context", "channel_context", "group_context", 
        "on_message", "on_event", "channel_only", "group_only", "private_only"
    ]  # 让 ruff 满意

from mqga.lookup.context import __getattr__ as __get_context_attr__

def __getattr__(name: str):
    return __get_context_attr__(name)
    # raise AttributeError

from mqga.event.on import on_message, on_event, channel_only, group_only, private_only
