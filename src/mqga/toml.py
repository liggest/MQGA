
from mqga.__version__ import __version__
from mqga.args import args
from mqga.log import log

import os
import sys
import tomli
import tomli_w
from pydantic import BaseModel

class Project(BaseModel):
    name: str = 'MQGA'
    version: str = __version__
    authors: list = ['Liggest','duolanda','liuyu.fang']
    description: str = 'Mostly a QQ Group Assistant'
    address: str = 'https://github.com/liggest/MQGA'
    license: str = 'MIT'
    license_file: str = 'LICENSE'
    copyright: str = 'Copyright (c) 2021 Liggest'
    


class Config(BaseModel):
    AppID: str = ''
    Token: str = ''
    Secret: str = ''
  
class Toml(BaseModel):
    Project: Project = Project()
    Config: Config = Config()



class Init():
    toml = Toml()
    def __init__(self, args: object):
        config_file = 'config.toml'
        save_file = config_file
        if args.config:
            config_file = args.config
        if os.path.exists(config_file):
            with open(config_file, "rb") as f:
                data = tomli.load(f).get("cofig", {})
                self.toml.Config.AppID = data.get("AppID",'')
                self.toml.Config.Token = data.get("Token",'')
                self.toml.Config.Secret = data.get("Secret",'')
        elif args.config:
            log.warning(" 未找到config文件")
        if args.dump:
            save_file = args.dump
        if args.appid:
            self.toml.Config.AppID = args.appid
        if args.token:
            self.toml.Config.Token = args.token
        if args.secret:
            self.toml.Config.Secret = args.secret
        if not self.toml.Config.AppID or not self.toml.Config.Secret:
            log.exception("appid, secret 必须输入才可使用该BOT")
            sys.exit(1)
        if args.config or not os.path.exists(save_file):
            data = self.toml.model_dump()
            with open(save_file, "wb") as f:
                tomli_w.dump(data, f)
            log.info("config文件已保存至: %s" % save_file)
        
        
config = Init(args).toml.Config