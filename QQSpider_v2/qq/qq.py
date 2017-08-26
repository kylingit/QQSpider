# -*- coding:utf-8 -*-

import requests


class QQ(object):
    def __init__(self, user, pwd):
        self.user = user
        self.pwd = pwd
        self.session = requests.Session()

    def g_tk(self):
        h = 5381
        cookies = self.session.cookies
        s = cookies.get('p_skey') or cookies.get('skey') or ''
        for c in s:
            h += (h << 5) + ord(c)
        return h & 0x7fffffff
