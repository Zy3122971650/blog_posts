---
title: 记一次在Github Action上使用SCP部署博客文章
date: 2021-4-22 18:03:59
tags:
 - SSH
 - Github Action
---
因为东搞一下，西搞一下的学习路径，欠下了很多技术债。最近在在Github Action上使用密钥连接服务器的时候就深有体会。

## 错误示范
1. 把privaly.key写入文件
2. 使用SCP远程传输文件

结果：报错

## 回想一下使用密钥的ssh流程
第一次连接某个服务器时，输入`ssh -i privaly.key username@host` 然后核对返回的目标服务器的指纹，按Y加入到known_hosts。

## 正确示范
1. 把privaly.key写入文件
2. 设置文件权限
3. 把指纹加入到known_hosts中
4. 使用SCP远程传输文件

这么突然多了一个设置文件权限，因为文件权限太大会被认为是不安全的，所以会拒绝使用这个私钥。

最后代码大概就是

```bash
    mkdir  ~/.ssh/
    echo -e "${{secrets.SERVER_KEY}}" > key.pem
    echo -e "${{secrets.SERVER_SSH_RAS}}" > ~/.ssh/known_hosts
    sudo chmod 600 key.pem
    scp -i key.pem -r dist ubuntu@${{ secrets.SERVER_IP }}:remote/path/
```
