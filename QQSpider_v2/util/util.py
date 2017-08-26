# -*- coding:utf-8 -*-
import os
import requests
import pickle
import random

"""
一些基本模块，与 cookie 操作和浏览器头相关
"""

path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
filename = '\cookies.txt'
cookie_file = path + filename


def save_cookie_to_file(cookie, cookie_file):
    """保存 cookie 到文件"""
    with open(cookie_file, 'wb') as f:
        pickle.dump(cookie, f)


def load_cookie_from_file(cookie_file):
    """从文件读取 cookie"""
    if os.path.isfile(cookie_file):
        with open(cookie_file, 'rb') as f:
            cookies = pickle.load(f)
        return cookies
    return None


def cookiejar_to_string(cookies):
    """把 cookiejar 对象转换为字符串"""
    if cookies is None:
        return None
    else:
        cookie = ''
        for item in cookies:
            cookie += item.name + '=' + item.value + '; '
        cookie = cookie[:len(cookie) - 2]
        return cookie


def get_cookie():
    """获取 cookie """
    s = requests.Session()
    cookies = load_cookie_from_file(cookie_file)
    if cookies is not None:
        for item in cookies:
            s.cookies.set(item['name'], item['value'])
        if s.cookies is not None:
            return s.cookies
    return None


cookie = cookiejar_to_string(get_cookie())

UAlist = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0"
]

headers = {
    'Host': 'h5.qzone.qq.com',
    'User-Agent': random.choice(UAlist),
    'Accept': '*/*',
    'Accept-Language': 'zh,zh-CN;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Cookie': cookie,
    'Connection': 'keep-alive'
}
