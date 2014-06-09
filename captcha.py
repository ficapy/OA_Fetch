#!/usr/bin/env python
#coding=utf-8
#Author:ficapy<c4d@outlook.com>
#website:http://zoulei.net
#Create on 2014-06-08

'''
对当前浏览器browser所定位的位置截取验证码图片 上传到网站获取验证码
'''
from PIL import Image
import requests
import re
import time
import tempfile
import ConfigParser
import codecs

cf = ConfigParser.ConfigParser()
cf.readfp(codecs.open('conf.ini','r','utf-8'))

username = cf.get('captcha','username')
pwd = cf.get('captcha','password')

def get_img(Browser,imgxpath):
    imgelement = Browser.find_element_by_xpath(imgxpath)
    location = imgelement.location
    size = imgelement.size
    tmppath = tempfile.mktemp(suffix='.png')
    Browser.save_screenshot(tmppath)
    im = Image.open(tmppath)
    left = location['x']
    top = location['y']
    right = left + size['width']
    bottom = location['y'] + size['height']
    im = im.crop((left, top, right, bottom))
    im.save(tmppath)
    return tmppath

def LZdm(username,passwd,imgpath):
    '''
    使用联众打码，输入用户名、密码、图片地址获取验证码
    '''
    url = 'http://bbb4.hyslt.com/index.php/demo/4356748'
    session = requests.Session()
    files = {'imagepath': open(imgpath, 'rb')}
    params = {
                "info[lz_user]" : username,
                "info[lz_pass]" : passwd,
                'pesubmit':''
    }
    tmp = session.post(url,data=params,files=files).text
    code = re.findall("window.location.href='http://bbb4.hyslt.com/demo/(\d+)'",tmp)[0]
    resurl = "http://bbb4.hyslt.com/index.php?mod=demo&act=result&id=%s"%code

    while True:
        # print('please wait...')
        time.sleep(0.5)
        res = session.get(resurl).json()
        try:
            if res['result']:
                return res['result']
                break
        except:
            pass

def get_captcha(Browser,imgxpath):
    img = get_img(Browser,imgxpath)
    captcha = LZdm(username,pwd,img)
    return captcha
