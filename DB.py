#!/usr/bin/env python
#coding=utf-8
#Author:ficapy<c4d@outlook.com>
#website:http://zoulei.net
#Create on 2014-06-08

import sqlite3

'''
对数据库操作进行简易包装，写入 查询 输出生成图表所需要的raw_datas()
只支持单步操作、每调用一次会执行commit close操作
生成rawdata表 含项目名称、数据、流程是否完成
'''


def insert(project,data,isdone):
    conn = sqlite3.connect('OA.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rawdata
                (project TEXT NOT NULL UNIQUE,
                data TEXT,
                isdone TEXT)
                ''')
    try:
        c.execute('insert into rawdata values (?,?,?)',(project,data,isdone))
    except Exception as e:
        pass
    finally:
        conn.commit()
        conn.close()

def update(project,data,isdone):
    conn = sqlite3.connect('OA.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rawdata
                (project TEXT NOT NULL UNIQUE,
                data TEXT,
                isdone TEXT)
                ''')
    try:
        c.execute('update rawdata set data=?,isdone=? where project=?',(data,isdone,project))
    except Exception as e:
        print e
        pass
    finally:
        conn.commit()
        conn.close()

def done():
    '''
    返回已完成项目名称列表，以便和抓取到的列表进行对比，对已完成的项目则跳过再次抓取
    '''
    conn = sqlite3.connect('OA.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rawdata
                (project TEXT NOT NULL UNIQUE,
                data TEXT,
                isdone TEXT)
                ''')
    done = [i[0] for i in c.execute('select project from rawdata where isdone="1"').fetchall()]
    conn.commit()
    # self.conn.close()
    return done

def all():
    conn = sqlite3.connect('OA.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rawdata
                (project TEXT NOT NULL UNIQUE,
                data TEXT,
                isdone TEXT)
                ''')
    all = [i[0] for i in c.execute('select project from rawdata').fetchall()]
    conn.commit()
    conn.close()
    return all

def output_data():
    conn = sqlite3.connect('OA.db')
    c = conn.cursor()
    all = c.execute('select project,data from rawdata').fetchall()
    conn.commit()
    conn.close()
    if len(all)>13:
        return [[i[0],eval(i[1])] for i in all[-14:]]
    else:
        return [[i[0],eval(i[1])] for i in all]

# print output_data()

