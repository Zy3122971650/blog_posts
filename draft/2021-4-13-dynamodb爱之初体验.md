---
title: dynamodb爱之初体验
date: 2021-4-13 22:18:50
tags:
 - dynamodb
 - 技术
 - 亚马逊
---

为啥我要使用dynamoDB呢？当然是因为~~出于对技术的热爱~~可以白嫖。

以下对dynamoDB的操作基于`Python3`
## 连接到dynamoDB
### 申请IAM
在使用SDK和Amazon CLI的时候需要验证身份，在IAM服务中添加一个用户，得到你用来验证身份的`AWS_ACCESS_KEY_ID`和`AWS_SECRET_ACCESS_KEY`

### 安装适用Python3的SDK
```bash
    python3 -m pip install boto3
```

### 创建连接
```python
import boto3
dynamodb = boto3.resource('dynamodb',
                          region_name='ap-northeast-1',
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          )

```

## 创建表
创建一个表你需要指定`TableName` `KeySchema` `AttributeName` `ProvisionedThroughput`

## 插入数据

## 读取数据

## 更新数据

## 删除数据