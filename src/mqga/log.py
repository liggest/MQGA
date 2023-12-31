import os
import sys
import logging
from mqga.args import args
from time import strftime

BOOTPath = os.getcwd()
PATH = os.path.abspath('.') + '/log/'
DEFAULT_LOGGER_NAME = "MQGA"

# \033[3xm x的取值范围0-7，分别对应下面几种颜色
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

COLORS = {
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
Console_FMT = "\033[1;38m[\033[0m%(levelname)s \033[1;38m<- %(pathname)s:%(lineno)s]\033[0m %(message)s"
File_FMT = "[%(levelname)s <-%(pathname)s:%(lineno)s]\n%(asctime)s: %(message)s"

# 变更等级颜色
class ColoredFormatter(logging.Formatter):
    def __init__(self, msg):
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


class MQGALog(object):
    def __init__(self):
        if not os.path.exists(PATH):
            os.mkdir(PATH)
        self.logger = logging.getLogger(DEFAULT_LOGGER_NAME)
        # self.file_formatter = logging.Formatter(fmt=File_FMT, datefmt=DATEFMT)
        self.log_filename = '{0}{1}.log'.format(PATH, strftime("%Y-%m-%d"))
    
        self.file_handler = self.get_file_handler(self.log_filename)
        self.std_handler = self.get_console_handler(False)
        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.std_handler)

        self.logger.setLevel(logging.INFO)

    def get_file_handler(self, filename):
        filehandler = logging.FileHandler(filename, encoding="utf-8")
        filehandler.setFormatter(FileFormatter(File_FMT, DATEFMT))
        return filehandler


    def get_console_handler(self, is_debug: bool):
        if is_debug:
            fmt = Console_FMT
        else:
            fmt = Default_FMT
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColoredFormatter(fmt))
        return console_handler
    
    def set_debug(self):
        self.logger.setLevel(logging.DEBUG)
        self.logger.removeHandler(self.std_handler)
        self.std_handler = self.get_console_handler(True)
        self.logger.addHandler(self.std_handler)

logset = MQGALog()
if args.debug:  # 设置log输出样式
    logset.set_debug()
log = logset.logger
if args.debug:  # 设置log输出样式
    log.debug("已进入debug mode")

