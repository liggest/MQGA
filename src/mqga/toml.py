from __future__ import annotations
from mqga.__version__ import __version__
from mqga.args import parser, args
from mqga.log import log

import os
import sys
import tomli
import tomli_w
from pydantic import BaseModel

class Project(BaseModel):
    name: str = 'MQGA'
    version: str = __version__
    authors: list = ['liggest','duolanda','liuyu.fang']
    description: str = 'Mostly a QQ Group Assistant'
    address: str = 'https://github.com/liggest/MQGA'
    license: str = 'MIT'
    license_file: str = 'LICENSE'
    copyright: str = 'Copyright (c) 2021 liggest'
    


class Config(BaseModel):
    AppID: str = ''
    Token: str = ''
    Secret: str = ''
    Public: bool = False
    Sandbox: bool = False
  
class Toml(BaseModel):
    project: Project = Project()
    config: Config = Config()



class Init():
    toml = Toml()
    def __init__(self, args):
        config_file = 'config.toml'
        save_file = config_file
        if args.config:
            config_file = args.config
        if args.dump:
            save_file = args.dump
        if os.path.exists(config_file):
            with open(config_file, "rb") as f:
                data:dict = tomli.load(f).get("config", {})
                self.toml.config.AppID = data.get("AppID",'')
                self.toml.config.Token = data.get("Token",'')
                self.toml.config.Secret = data.get("Secret",'')
                self.toml.config.Public = data.get("Public",False)
                self.toml.config.Sandbox = data.get("Sandbox",False)
            log.info(f"读取到 {config_file} 文件数据,将以其内容启动bot")
        elif args.config:
            log.warning("未找到config文件")
        if args.appid or args.token or args.secret or args.public or args.sandbox:
            log.info('检测输入了参数,将优先选取参数执行')
            if args.appid:
                self.toml.config.AppID = args.appid
            if args.token:
                self.toml.config.Token = args.token
            if args.secret:
                self.toml.config.Secret = args.secret
            if args.public:
                self.toml.config.Public = args.public
            if args.sandbox:
                self.toml.config.Sandbox= args.sandbox
        if not self.toml.config.AppID or not self.toml.config.Secret:
            log.error("appid, secret 必须输入才可使用该BOT\n")
            parser.print_help()
            sys.exit(1)
        if args.dump or not os.path.exists(save_file):
            data = self.toml.model_dump()
            with open(save_file, "wb") as f:
                tomli_w.dump(data, f)
            if args.dump:
                log.info("已保存config文件至: %s" % save_file)
            else:
                log.info("数据已自动保存至: %s ,下次可直接启动bot" % save_file)
        
        
config = Init(args).toml.config

