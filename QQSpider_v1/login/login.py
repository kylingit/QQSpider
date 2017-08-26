#-*- coding:utf-8 -*-

import os
import qqlib
from qqlib import qzone
import requests, requests.utils, cookielib
from util import util

class Login(object):
	def __init__(self, user, pwd):
		self.qq = qzone.QZone(user, pwd)

	def login(self):
		exc = None
		while True:
			try:
				if exc is None:
					self.qq.login()
					break
				else:
					verifier = exc.verifier
					open('verify.jpg', 'wb').write(verifier.fetch_image())
					print('saved verify.jpg')
					vcode = input('input verify(e.g.\'ABCD\'): ')
					verifier.verify(vcode)
					exc = None
			except qqlib.NeedVerifyCode as e:
				if e.message != None:
					print e.message
				exc = e

	def check_login(self, qq, cookie):
		s = qq.session
		if 'uin' in cookie and qq.user in cookie.get('uin'):
			s.cookies = cookie
		else:
			print 'cookies was unavailable, please delete the cookies file and try again.'
			return False
		
		g_tk = str(qq.g_tk())
		url = 'https://h5.qzone.qq.com/proxy/domain/r.qzone.qq.com/cgi-bin/user/cgi_personal_card?uin=' + qq.user + '&g_tk=' + g_tk
		header = util.headers
		r = s.get(url, headers = header)
		if r.content.find('登录') > 0:
			print 'cookies was xpired, please delete the cookies file and try again.'
			return False
		else:
			print 'login succeed.'
			try:
				print 'Hi, ' + eval(r.content[10:-3]).get('nickname').decode('utf-8').encode('GB18030')
			except:
				print 'sorry, name cannot display'		#some nickname cannot display in terminal, such as emoji
			return True

	def login_test(self):
		s = self.qq.session
		cookie_file = util.cookie_file
		if util.cookie == None:
			print 'login...'
			self.login()
			util.save_cookie_to_file(s.cookies, cookie_file)
			cookies = s.cookies
		else:
			print 'trying login by cookies...'
			cookies = util.get_cookie()

		return self.check_login(self.qq, cookies)
