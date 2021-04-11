# 折腾理由

之前用小米路由器刷过Padavan固件以用于科学上网，后面因为这台路由器的配置太低使得科学上网很慢所以搁置了。现在入手了一个iphone6s，由于IOS的特性（v2ray的软件要钱以及各种折腾），便把手上的树莓派用了起来。

其次，N年前的小米mini跑起v2ray来确实有点头疼。
# 原理
利用iptables把进入树莓派的未标记的流量定向到v2ray，而从V2ray中出来的流量会被打上标记，被放行。

防止了流量的回环
# 材料
- 树莓派
- 一台正在使用的路由器
- 一颗愿意动手的心
- Google/Baidu


# 我的环境

- 电脑用的 Linux
- 树莓派用的Ubuntu arm

如果你在Windows10下的话，打开你的Cmd/Powershell试试ssh命令是否可用。

不然你可能需要去使用Xshell/Putty之类的用于连接树莓派。

我相信都手拿树莓派的你，一定可以搞定这些小问题

# 教程开始
## 安装必须的软件
- V2ray
- Dnsmasq
### V2ray

既然都打算`v2ray配合Pi3b+`搭透明网关来科学上网了，这不在话下吧。
利用自动安装脚本（鉴于文章不在V2ray上扩展）
```bash
bash <(curl -L -s https://install.direct/go.sh)
```

### Dnsmasq

这个就简单了嘛，仓库里都有。
```bash
apt install dnsmasq
```

## 开启网卡的转发

```bash
echo net.ipv4.ip_forward=1 >> /etc/sysctl.conf && sysctl -p
```

## V2ray的配置

以下是我的V2ray配置。

功能还包含分流DNS查询，以防访问国外网站时发生欺骗

关键点是要有一个任意门用来接受iptables转发来的流量（要设置tproxy），其次是流量在出去的时候要打上标记。
```json
{  
    "log": {
        "loglevel": "info",
        "access": "/root/v2ray.log"
    },
    "inbounds": [
        {   
            "tag": "transparent",
            "port": 1083,
            "protocol": "dokodemo-door",
            "settings": {
                "network": "tcp,udp",
                "followRedirect": true
            },
            "sniffing": {
                "enabled": true,
                "destOverride": [
                    "http",
                    "tls"
                ]
            },
            "streamSettings": {
                "sockopt": {
                    "tproxy": "tproxy"

                }
            }
        },
        {
            "listen": "0.0.0.0",
            "port": 2333,
            "protocol": "mtproto",
            "settings": {
                "users": [
                    {
                        "email": "123@123.com",
                        "secret": "UUID"
                    }
                ]
            },
            "tag": "tg_in"
        },
        {
            "listen": "127.0.0.1",
            "port": 1080,
            "protocol": "socks",
            "sniffing": {
                "enabled": true,
                "destOverride": [
                    "http",
                    "tls"
                ]
            },
            "settings": {
                "auth": "noauth"
            }
        },
        {
            "listen": "192.168.3.59",
            "port": 1081,
            "protocol": "http",
            "tag": "http_in"
        }
    ],
    "outbounds": [
        {
          ######你的出站代理
            "tag": "proxy"
        },
        {
            "tag": "tg_out",
            "protocol": "mtproto",
            "proxySetting": "proxy"
        },
        {
            "tag": "direct",
            "protocol": "freedom",
            "streamSettings": {
                "sockopt": {
                    "mark": 255
                }
            }
        },
        {
            "tag": "block",
            "protocol": "blackhole",
            "settings": {
                "response": {
                    "type": "http"
                }
            }
        },
        {
            "tag": "dns-out",
            "protocol": "dns",
            "streamSettings": {
                "sockopt": {
                    "mark": 255
                }
            }
        }
    ],
    "dns": {
        "servers": [
            {
                "address": "1.1.1.1",
                "port": 53,
                "domains": [
                 "geosite:geolocation-!cn"
                ],
                "expectIPs": [
                  "geoip:cn"
                ]
              },
            {
                "address": "114.114.114.114",
                "port": 53,
                "domains":[
                  "geosite:cn"
                ]
              },
            "233.5.5.5",
            "114.114.114.114"
        ]
    },
    "routing": {
        "domainStrategy": "IPOnDemand",
        "rules": [
            {
                "type": "field",
                "inboundTag": [
                    "transparent"
                ],
                "port": 5353,
                "network": "udp",
                "outboundTag": "dns-out"
            },
            {
                "type": "field",
                "inboundTag": [
                    "transparent"
                ],
                "port": 123,                 /ntp服务器用到的端口，直连防止同步时间时出现太大的误差导致v2ray不可用
                "network": "udp",
                "outboundTag": "direct"
            },
            {
                "type": "field",
                "inboundTag": [
                    "tg_in"
                ],
                "outboundTag": "tg_out"
            },
            {
                "type": "field",
                "ip": [
                    "223.5.5.5",
                    "114.114.114.114"
                ],
                "outboundTag": "direct"
            },
            {
                "type": "field",
                "ip": [
                    "8.8.8.8",
                    "1.1.1.1"
                ],
                "outboundTag": "proxy"
            },
            {
                "type": "field",
                "protocol": [
                    "bittorrent"
                ],
                "outboundTag": "direct"
            },
            {
                "type": "field",
                "ip": [
                    "geoip:private",
                    "geoip:cn"
                ],
                "outboundTag": "direct"
            },
            {
                "type": "field",
                "domain": [
                    "geosite:cn"
                ],
                "outboundTag": "direct"
            }
        ]
    }
}

```
## Dnsmasq配置
因为在这里我是把Dnsmasq架设在53端口上的，所以需要关掉systemd-slove服务
```bash
systemctl disable systemd-slove
systemctl stop systemd-slove
```

然后更改位于/etc/dnsmasq.conf的配置文件（没有的话直接创建即可）

```conf
port=53
no-poll #不接受上游服务器的更新
no-resolv 
#server=114.114.114.114
server=192.168.3.59#5353                             #如果缓存中没有对应的ip则向V2ray查询
cache-size=5000
min-cache-ttl=3600                                          #改变缓存时间，不知道实际上有无用
```

启动Dnsmasq服务

```
systemctl enable dnsmasq
systemctl start dnsmasq
```

现在用下面进行DNS查询两次，第二次返回时间应该0-2ms之内。

```bash
drill www.baidu.com
#或者
nslook
```

如果不是这个结果，可能需要查看\etc\reslove.conf指定namesever 为 127.0.0.1

```conf
nameserver 127.0.0.1
```

## iptables规则
这个规则会在重启的时候清除，后面会附带一个自动配置的server
``` bash
# 代理局域网设备
iptables -t mangle -N V2RAY
iptables -t mangle -A V2RAY -d 127.0.0.1/32 -j RETURN
iptables -t mangle -A V2RAY -d 224.0.0.0/4 -j RETURN
iptables -t mangle -A V2RAY -d 255.255.255.255/32 -j RETURN
iptables -t mangle -A V2RAY -d 192.168.0.0/16 -p tcp -j RETURN # 直连局域网，避免 V2Ray 无法启动时无法连网关的 SSH，如果你配置的是其他网段（如 10.x.x.x 等），则修改成自己的
iptables -t mangle -A V2RAY -d 192.168.0.0/16 -p udp ! --dport 5353 -j RETURN # 直连局域网，53 端口除外（因为要使用 V2Ray 的 
iptables -t mangle -A V2RAY -p udp -j TPROXY --on-port 1083 --tproxy-mark 1 # 给 UDP 打标记 1，转发至 12345 端口
iptables -t mangle -A V2RAY -p tcp -j TPROXY --on-port 1083 --tproxy-mark 1 # 给 TCP 打标记 1，转发至 12345 端口
iptables -t mangle -A PREROUTING -j V2RAY # 应用规则

# 代理网关本机
iptables -t mangle -N V2RAY_MASK
iptables -t mangle -A V2RAY_MASK -d 224.0.0.0/4 -j RETURN
iptables -t mangle -A V2RAY_MASK -d 255.255.255.255/32 -j RETURN
iptables -t mangle -A V2RAY_MASK -d 192.168.0.0/16 -p tcp -j RETURN # 直连局域网
iptables -t mangle -A V2RAY_MASK -d 192.168.0.0/16 -p udp ! --dport 5353 -j RETURN # 直连局域网，53 端口除外（因为要使用 V2Ray 的 DNS）
iptables -t mangle -A V2RAY_MASK -j RETURN -m mark --mark 0xff    # 直连 SO_MARK 为 0xff 的流量(0xff 是 16 进制数，数值上等同与上面V2Ray 配置的 255)，此规则目的是避免代理本机(网关)流量出现回环问题
iptables -t mangle -A V2RAY_MASK -p udp -j MARK --set-mark 1   # 给 UDP 打标记,重路由
iptables -t mangle -A V2RAY_MASK -p tcp ! --dport 22 -j MARK --set-mark 1   # 给 TCP 打标记，重路由
iptables -t mangle -A OUTPUT -j V2RAY_MASK # 应规则
```

## 设置树莓派的默认网关
因为接下来要在路由器更改默认网关为树莓派，如果树莓派不绑定路由器的地址为默认网关的话，流量就出不去啦！

```bash
ip route add default via  192.168.3.1  dev eth0 #eth0是网卡名称，192.168.3.1是我路由器的地址
```

## 配置路由器
- 为树莓派绑定静态ip
- 设置dhcp服务的默认网关为树莓派的ip地址
  
## 拿出你的手机试一试能不能科学的上网了
不行的话你可能要去参考那些帮助我完成配置的文章了。因为我这里还没搞评论功能 - -

## 写好的systemd server

先把iptables的内容保存到一个文档里面

然后在\etc\systemd\system建立一个xxx.server文件，把下面的命令复制进去

```bash
[Unit]
Description=V2Ray tproxy Service
After=network.target
Wants=network.target

[Service]
Type=oneshot
ExecStart=/bin/bash /root/iptables_rules ; /sbin/ip route add default via  192.168.3.1  dev eth0  

[Install]
WantedBy=multi-user.target
```

不要忘记把它加入到开启启动

```bash
systemctl enable xxx.server
```

到此为止应该是结束了。

# 感谢
感谢那些在网络上乐于分享的人们

参考资料
- [官方的白话文教程](https://toutyrater.github.io/app/tproxy.html)
- [某位大佬的一份教程和打包好的镜像](https://github.com/MassSmith/smgate/wiki/%E6%A0%91%E8%8E%93%E6%B4%BE%E9%80%8F%E6%98%8E%E7%BF%BB%E5%A2%99%E7%BD%91%E5%85%B3%E8%AE%BE%E7%BD%AE)
- [漫谈DNS技术黑科技](https://medium.com/@TachyonDevel/%E6%BC%AB%E8%B0%88%E5%90%84%E7%A7%8D%E9%BB%91%E7%A7%91%E6%8A%80%E5%BC%8F-dns-%E6%8A%80%E6%9C%AF%E5%9C%A8%E4%BB%A3%E7%90%86%E7%8E%AF%E5%A2%83%E4%B8%AD%E7%9A%84%E5%BA%94%E7%94%A8-62c50e58cbd0)
- [DNS及其应用](https://steemit.com/cn/@v2ray/dns)