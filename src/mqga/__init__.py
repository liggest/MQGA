
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
