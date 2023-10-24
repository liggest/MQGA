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
pdm run pytthon bot.py [-Tadhst] ID1 ID2 ...

  -D    
        enable debug-level log output
  -a string
        qq 机器人ID
  -s string
        qq 机器人密钥
  -t string
        qq 机器人令牌
  -p
        only listen to public intent
  -b
        run in sandbox api
  -c string
        load from config
  -d string
        save bot config to filename (eg. config.toml)
  -h    
        print this help
```

  其中 qq 机器人ID、密钥、令牌 在 https://q.qq.com/bot/#/developer/developer-setting 获取

  第一次使用时如果没有导入config文件,将会以参数保存到config.toml,下次启动bot可以不需要再次传参.
  
  指令参数优先级: bot参数 > 指定config文件 > 默认config文件

