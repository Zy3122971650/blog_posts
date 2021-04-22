#! /usr/bin/python3

import sys
import time
import os


fileName = sys.argv[1]
localTime = time.localtime(time.time())

os.chdir('normal')

if os.path.exists(time.strftime("%Y-%m-%d")+'-'+fileName+'.md'):
    print("文件已经存在啦！！")
    exit(0)

with open(time.strftime("%Y-%m-%d")+'-'+fileName+'.md', 'w+') as f:
    stLocalTime = time.strftime("%Y-%m-%d %H:%M:%S")
    font = ['---', 'title: '+fileName,
            'date: '+stLocalTime, 'tags:\n - null', '---']
    f.write("\n".join(font))
