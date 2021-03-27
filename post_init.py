#! /usr/bin/python

import sys
import time
import os


fileName = sys.argv[1]
localTime = time.localtime(time.time())

os.chdir('normal')

if os.path.exists("{}-{}-{}-".format(localTime[0], localTime[1],
                                     localTime[2])+fileName+'.md'):
    print("文件已经存在啦！！")
    exit(0)

with open("{}-{}-{}-".format(localTime[0], localTime[1],
                             localTime[2])+fileName+'.md', 'w+') as f:
    stLocalTime = "{}-{}-{} {}:{}:{}".format(localTime[0], localTime[1],
                                             localTime[2], localTime[3], localTime[4], localTime[5])
    font = ['---', 'title: '+fileName,
            'date: '+stLocalTime, 'tag: null', '---']
    f.write("\n".join(font))
