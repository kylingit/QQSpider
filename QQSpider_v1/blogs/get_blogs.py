#-*- coding:utf-8 -*-

from util import util

class Get_blogs(object):
	def __init__(self):
		self.header = util.headers
		self.cookie = util.cookie

	def get_blogs(self, qq, cookie):
		s = qq.session
		s.cookies = cookie
		g_tk = str(qq.g_tk())
		header = self.header
		url = 'https://h5.qzone.qq.com/proxy/domain/b11.qzone.qq.com/cgi-bin/blognew/get_abs?hostUin=' + qq.user + '&uin=' + qq.user +\
			'&blogType=0&statYear=2017&reqInfo=7&num=15&g_tk=' + g_tk
		print url
		r = s.get(url, headers = header)
		return r.content