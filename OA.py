#!/usr/bin/env python
#coding=utf-8
#Author:ficapy<c4d@outlook.com>
#website:http://zoulei.net
#Create on 2014-06-08

import time
import re
import codecs
import ConfigParser
from Tkinter import _flatten
import sys

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

from captcha import get_captcha
import DB


cf = ConfigParser.ConfigParser()
cf.readfp(codecs.open('conf.ini','r','utf-8'))

url = cf.get('OA','url')                    #公司网址
username = cf.get('OA','username')          #用户名
password = cf.get('OA','password')          #密码


browser = webdriver.Ie()
browser.maximize_window()
browser.set_page_load_timeout(60)
browser.implicitly_wait(60)

def click_element(id):
    """
    在IEdriver上直接对javascript脚本进行get操作会阻塞，以致后面的操作无法进行
    单独对这个操作设置2秒超时，后面复位到20秒
    """
    browser.set_page_load_timeout(3)
    try:
        if u'证书' in browser.title:
            browser.get('javascript:document.getElementById("{}").click()'.format(id))
        else:
            while True:
                if browser.find_element_by_id(id):
                    browser.get('javascript:document.getElementById("{}").click()'.format(id))
                    break
    except:
        pass
    browser.set_page_load_timeout(60)

def fill_usn_pwd():
    time.sleep(3)
    browser.find_element_by_id('svpn_name').send_keys(username)
    browser.find_element_by_id('svpn_password').send_keys(password)
    time.sleep(3)
    # captcha_auto = get_img(browser,"//td[@valign='middle']/img")
    captcha_auto = get_captcha(browser,"//td[@valign='middle']/img")
    print u'验证码为：',captcha_auto
    # captcha_hand = raw_input(u'请手动输入四位验证码：')
    time.sleep(3)
    browser.find_element_by_id('randcode').send_keys(captcha_auto)
    browser.find_element_by_class_name('btn_off').submit()
    time.sleep(3)
    try:
        browser.switch_to_alert().accept()
        return False
    except:
        return True


def login():
    browser.get(url)
    time.sleep(3)
    # 采用javascript方法，来点击“继续浏览此网站(不推荐)。 ”链接
    click_element('overridelink')
    #最多尝试输入验证码3次，否则退出
    fail_number =0
    while 1:
        fail_number+=1
        if fail_number>= 4:
            browser.quit()
            sys.exit()
        elif fill_usn_pwd():
            break

    #加载速度巨慢，老实等20秒吧,否则后面容易出错
    time.sleep(20)
    #计数60秒等待主界面
    count = 1
    while 1:
        if browser.title == u'富力信息门户':
            print u'登陆成功'
            return True
            break
        elif count > 61:
            print u'网络爆慢，登陆失败'
            return False
            break
        time.sleep(1)
        count+=1


def check_msg():
    '''
    在新窗口打开流程管理页面http://192.168.18.1:8899/iOffice/prg/fl/flDocList.aspx?flfoldid=1
    '''
    time.sleep(20)
    url = 'http://192.168.18.1:8899/iOffice/prg/fl/flDocList.aspx?flfoldid=1'
    browser.get(url)
    time.sleep(5)
    html = browser.page_source
    title_lists = re.findall(r'<TD><A class=td href="/iOffice/prg/fl/.+aspx">(.+?)</A></TD>',html)
    #列表去重操作
    title = list(set(title_lists))
    title.sort(key = title_lists.index)
    return title

def fetch_single_page(title):
    time.sleep(3)
    browser.find_element_by_link_text(title).send_keys(Keys.ENTER)
    time.sleep(3)
    #查找关注按钮，确定网页已成功加载以便获取html
    browser.find_element_by_id('ctl00_cntButton_Flowaction1_ioEmpFocusEventSet1_IoUpdatePanel1')
    html = browser.page_source
    soup = BeautifulSoup(html)
    hehe = soup.findAll(onmouseover = "javascript:if(this.bgColor!='#ccddee'){this.bgColor='#eeeeee';}")
    #WHITE-SPACE: nowrap
    #统计数据
    name_time = []
    for i in hehe:
        #忽略附件以及知会人员
        if i.parent.td.string == u'序号':
            try:
                # i['style']
                #遇到知会相关人员栏则跳过循环
                if u'知会相关人员' in str(i.findAll('td')[1].img):
                    break
            except:
                #没完全学会bs
                name = i.findAll('td')[2].a.text
                start_time =  i.findAll('td')[5].string.replace(u'\xa0',u'')
                end_time = i.findAll('td')[6].string.replace(u'\xa0',u'')
                process_time = end_time or start_time
                print title,name,process_time
                name_time.append((name,process_time.split()[0]))
    time.sleep(3)
    browser.back()
    time.sleep(2)
    return name_time

def main():
    login()
    titles = check_msg()
    #已完成列表
    done = DB.done()
    all = DB.all()
    for title in titles:
        print title
        if title not in done:
            craw = fetch_single_page(title)
            if cf.get('sheet','done_sign') in _flatten(craw):
                isdone = '1'
            else:
                isdone = '0'
            #项目在数据库中则更新，不存在则添加
            if title in all:
                DB.update(title,unicode(craw),isdone)
            else:
                DB.insert(title,unicode(craw),isdone)
            #特喵的操控IE就和伺候大爷一样啊
    browser.quit()


