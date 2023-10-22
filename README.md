<div align="center">
  <img src="src/迷途的羔羊.jpg" alt="迷途的羔羊" width = "256">
  <br><h1>MQGA</h1>“Mostly a QQ Group Assistant”</br>
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
        qq 机器人令牌
  -t string
        qq 机器人密钥
  -c string
        load from config
  -h    
        print this help
  -p
        only listen to public intent
  -b
        run in sandbox api
  -d string
        save bot config to filename (eg. config.yaml)
```
