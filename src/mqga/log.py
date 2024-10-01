import os
import re
import logging
from mqga.args import args
from logging.handlers import TimedRotatingFileHandler

BOOTPath = os.getcwd()
PATH = os.path.abspath('.') + '/log/'
DEFAULT_LOGGER_NAME = "MQGALog"

# \033[3xm x的取值范围0-7，分别对应下面几种颜色
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

TempLevel = 5
COLORS = {
    'TEMP': CYAN,
    'WARNING': YELLOW,
    'INFO': GREEN,
    'DEBUG': BLUE,
    'CRITICAL': RED,
    'ERROR': RED
}
"""LOGLevel = {
    0:'NOSET',
    10:'DEBUG',
    20:'INFO',
    30:'WARNING',
    40:'ERROR',
    50:'CRITICAL'
}"""

DATEFMT = '%Y-%m-%d %H:%M:%S'
Default_FMT = "\033[1;38m[\033[0m%(levelname)s\033[1;38m]\033[0m %(message)s"
Console_FMT = "\033[1;38m[\033[0m%(levelname)s \033[1;38mat %(pathname)s:%(lineno)s]\033[0m %(message)s"
File_FMT = "%(asctime)s | %(levelname)s | %(pathname)s:%(lineno)s : %(message)s"

# 变更等级颜色
class ColoredFormatter(logging.Formatter):
    def __init__(self, level):
        if level == TempLevel:
            msg = Console_FMT
        else:
            msg = Default_FMT
        logging.Formatter.__init__(self, msg)

    def format(self, record):
        levelname = record.levelname
        if levelname in COLORS:
            levelname_color = f"\033[1;3{COLORS[levelname]}m{levelname}\033[0m"
            record.levelname = levelname_color
        record.pathname = record.pathname.replace(BOOTPath, ".")
        return logging.Formatter.format(self, record)
    
class FileFormatter(logging.Formatter):
    def __init__(self, msg, datefmt):
        logging.Formatter.__init__(self, fmt=msg, datefmt=datefmt)

    def format(self, record):
        record.pathname = record.pathname.replace(BOOTPath, ".")
        return logging.Formatter.format(self, record)

# 建立log

class MQGALog(logging.Logger):
    def __init__(self, name):
        logging.Logger.__init__(self, name)

    def temp(self, message, *args, **kws):
        self.log(TempLevel, message, *args, **kws)

logging.setLoggerClass(MQGALog)
logging.addLevelName(TempLevel, 'TEMP')

# 创建log对象
_root = logging.getLogger()
log: MQGALog = logging.getLogger(DEFAULT_LOGGER_NAME)
log.setLevel(logging.DEBUG)

# 文件输出
if not os.path.exists(PATH):
    os.makedirs(PATH)
filehandler = TimedRotatingFileHandler(filename=f"{PATH}dump.log", when="midnight", interval=1, backupCount=7, encoding="utf-8")
filehandler.setLevel(logging.DEBUG)
filehandler.suffix = "%Y-%m-%d.log"
filehandler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}\.log$")
filehandler.setFormatter(FileFormatter(File_FMT, DATEFMT))
_root.addHandler(filehandler)  # 先挂到 root logger 上
# log.addHandler(filehandler)

# 控制台输出
console = logging.StreamHandler()
console.setLevel(logging.INFO)
if args.debug:
    console.setLevel(TempLevel)
console.setFormatter(ColoredFormatter(console.level))
_root.addHandler(console)
# log.addHandler(console)

# 调试模式
if args.debug:
    log.setLevel(TempLevel)
    log.temp("已进入DEBUG模式")
