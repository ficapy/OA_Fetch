#!/usr/bin/env python
#coding=utf-8
#Author:ficapy<c4d@outlook.com>
#website:http://zoulei.net
#Create on 2014-06-08

import OA
import DB
import Generator_sheet

#尝试登陆OA到达抓取数据页面，保存数据到数据库
OA.main()
#将数据输出
raw_datas = DB.output_data()
#生成图表
Generator_sheet.Generator_sheet(raw_datas)