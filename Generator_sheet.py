#!/usr/bin/env python
#coding=utf-8
#Author:ficapy<c4d@outlook.com>
#website:http://zoulei.net
#Create on 2014-06-08
#部分参考：http://stackoverflow.com/questions/21397549/stack-barh-plot-in-matplotlib-and-add-label-to-each-section-and-suggestions

from Tkinter import _flatten
import re
import datetime
import ConfigParser
import codecs
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt

#凑成如下数据结构输入
#raw_data=[[project1,[(name1,time1),(name2,time2)]],
#           [project2,[(name1,time1),(name2,time2)]],
#           。。。。。。。。。
# ]

patch_handles = []
def Generator_sheet(raw_data):
    cf = ConfigParser.ConfigParser()
    cf.readfp(codecs.open('conf.ini','r','utf-8'))

    #竖条宽度
    width = 0.8
    #加载中文字体让正常显示
    font = FontProperties(fname="simsun.ttc", size=14)
    colors ='brcmyw'
    #流程完成标志
    done_sign = cf.get('sheet','done_sign')

    project = [i[0] for i in raw_data]
    #将每个project字符插入换行符
    n=5
    project = ['\n'.join(re.findall(r'.{%d}|.{1,%d}$'%(n,max(1,len(i)%n)),i)) for i in project]
    name_and_times = [i[1] for i in raw_data]
    names = [[y[0] for y in x] for x in name_and_times]
    #压平names
    name = _flatten(names)
    times = [[y[1][2:].replace('-','.') for y in x] for x in name_and_times]
    times = _flatten(times)
    number = [[1]*len(i[1]) for i in raw_data]
    #为设置超时提醒做准备
    time_out = [len(i[1]) for i in raw_data]
    time_out_detection = []
    Initial = 0
    for i in time_out:
        Initial+=i
        time_out_detection.append(Initial)
    #是否符合添加需求(True表示需要添加提醒)
    vaild = [done_sign not in _flatten(i) for i in names]
    #需要提醒的位置
    need_alert = [vaild[x]*y for x,y in enumerate(time_out_detection)]
    #计算2个时间之间的差值,例如符合14.04.10离今天的时间
    def distance(timev):
        timev = '20'+timev
        ymd = [int(i) for i in timev.split('.')]
        d_now = datetime.datetime.now()
        d_2 = datetime.datetime(ymd[0],ymd[1],ymd[2])
        return (d_now-d_2).days



    def singlebar(left,height):
        global patch_handles
        bottom = 0
        #初始化出现标记位置
        sign = 10000
        for i,j in enumerate(height):
            if raw_data[-1][-1][i][0] == done_sign:
                patch_handles.append(plt.bar(left,j,width=width,align='center',color='g',bottom=bottom))
                #记住该位置
                sign = i
            elif i>sign:
                patch_handles.append(plt.bar(left,j,width=width,align='center',color='g',bottom=bottom))
            else:
                patch_handles.append(plt.bar(left,j,width=width,align='center',color=colors[i%len(colors)],bottom=bottom))
            bottom+=j

    #画图
    for x in xrange(len(number)):
        singlebar(x,number[x])

    #添加文字
    for j in xrange(len(patch_handles)):
        for i,patch in enumerate(patch_handles[j].get_children()):
            bl = patch.get_xy()
            x = 0.5*patch.get_width() + bl[0]
            y = 0.5*patch.get_height() + bl[1]
            if j+1 in need_alert and j>1:
                plt.text(x,y+0.1, "%s" % (name[j]), ha='center',fontproperties=font )
                plt.text(x,y-0.2, "%s" % (times[j]), ha='center',fontproperties=font )
                #添加提醒文字
                plt.text(x,y+0.6, u'已过%d天'%(distance(times[j])), ha='center',fontproperties=font,color ='r' )
            else:
                plt.text(x,y+0.1, "%s" % (name[j]), ha='center',fontproperties=font )
                plt.text(x,y-0.2, "%s" % (times[j]), ha='center',fontproperties=font )

    plt.xticks(range(len(number)),project,fontproperties=font)
    plt.title(cf.get('sheet','title'),fontproperties=font,size=30)
    plt.axis([-1,14,0,9])

    fig = plt.gcf()
    fig.set_size_inches(18.5,10.5)
    fig.subplots_adjust(left=0.02,bottom=0.17,right=0.99,top=0.93)
    fig.savefig('{}.png'.format(str(datetime.date.today())),dpi=600)
