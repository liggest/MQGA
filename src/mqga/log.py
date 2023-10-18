import os
import sys
import logging
from time import strftime

PATH = os.path.abspath('.') + '/log/'
DATEFMT = '%Y-%m-%d %H:%M:%S'
DEFAULT_LOGGER_NAME = "MQGA"
Console_FMT = "\033[1;33m[%(levelname)s -> %(filename)s:%(lineno)s]\033[0m %(asctime)s: %(message)s"
File_FMT = "[%(levelname)s -> %(filename)s:%(lineno)s] %(asctime)s: %(message)s"


class MQGALog(object):
    def __init__(self):
        if not os.path.exists(PATH):
            os.mkdir(PATH)
        self.logger = logging.getLogger(DEFAULT_LOGGER_NAME)
        self.console_formatter = logging.Formatter(fmt=Console_FMT, datefmt=DATEFMT)
        self.file_formatter = logging.Formatter(fmt=File_FMT, datefmt=DATEFMT)
        self.log_filename = '{0}{1}.log'.format(PATH, strftime("%Y-%m-%d"))

        self.logger.addHandler(self.get_file_handler(self.log_filename))
        self.logger.addHandler(self.get_console_handler())

        self.logger.setLevel(logging.DEBUG)

    def get_file_handler(self, filename):
        filehandler = logging.FileHandler(filename, encoding="utf-8")
        filehandler.setFormatter(self.file_formatter)
        return filehandler


    def get_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.console_formatter)
        return console_handler
   
log = MQGALog().logger