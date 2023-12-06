<div align="center">
  <img src="src/迷途的羔羊.jpg" alt="迷途的羔羊" width = "256">
  <br><h1>MQGA</h1>“Mostly a QQ Group Assistant”<br><br>
  
  [![tencent-guild](https://img.shields.io/badge/%E9%A2%91%E9%81%93-MQGA-yellow?style=flat-square&logo=tencent-qq)](https://pd.qq.com/s/dsremvwtg)
  
</div>

## Instructions

> Note: This framework is built mainly for Chinese users thus may display hard-coded Chinese prompts during the interaction.

参见 QQ 官方[文档](https://bot.q.qq.com/wiki/)。

## 安装
> 安装python3.10+
```bash
pip install pdm
# cd到项目目录
pdm install
```
## 命令行参数
> `[]`代表是可选参数
```bash
pdm bot [-Tadhst] ID1 ID2 ...

  -a string
        appid -> qq 机器人ID
  -s string
        secret -> qq 机器人密钥
  -t string
        token -> 机器人令牌
  -p
        public -> only listen to public intent
  -b
        sandbox -> run in sandbox api
  -c string
        config -> load config from config file
  -d string
        dump -> save bot config to filename (eg. config.toml)
  -h    
        help -> print MQGA help
  -D    
        debug -> set log to debug-level output
  -L    
        legacy -> used old qqbot api 
  -R    
        reload -> enable auto reloading mode
```

  其中 qq 机器人ID、密钥、令牌 在 https://q.qq.com/bot/#/developer/developer-setting 获取

  第一次使用时如果没有导入config文件,将会以参数保存到config.toml,下次启动bot可以不需要再次传参.
  
  指令参数优先级: bot参数 > 指定config文件 > 默认config文件

## 插件管理
> TODO, 持续开发中
