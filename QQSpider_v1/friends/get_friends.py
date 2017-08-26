#-*- coding:utf-8 -*-

import json, time
from util import util

class Get_friends(object):
	def __init__(self):
		self.header = util.headers
		self.cookie = util.cookie

	def get_friends(self, qq, cookie, db):
		self.db = db
		s = qq.session
		s.cookies = cookie
		g_tk = str(qq.g_tk())
		url = 'https://h5.qzone.qq.com/proxy/domain/r.qzone.qq.com/cgi-bin/tfriend/friend_show_qqfriends.cgi?uin='  + qq.user + '&fupdate=1&outCharset=utf-8&g_tk=' + g_tk
		header = self.header
		r = s.get(url, headers = header)
		dict = self.data2json(r.content[10:-2].strip().replace('\r\n','').replace('\\',''))
		id = 0
		for friends in dict['data']['items']:
			friendsdetail = self.get_friends_detail(qq, cookie, friends['uin'])
			if friendsdetail != '':
				data = {'id': id,
					'uin': friends['uin'],
					'sex': friendsdetail['sex'],
					'groupid': friends['groupid'],
					'nickname': friends['name'],
					'remark': friends['remark'],
					'spacename': friendsdetail['spacename'].replace('"','').replace('\\',''),
					'age': friendsdetail['age'],
					'birthday': str(friendsdetail['birthyear']) + '-' + friendsdetail['birthday'],
					'city': friendsdetail['country']+friendsdetail['province']+friendsdetail['city'],
					'img': friends['img'],
					'yellow': friends['yellow'],
					'online': friends['online'],
					'v6': friends['v6']}
			else:
				data = {'id': id,
					'uin': friends['uin'],
					'sex': 0,
					'groupid': friends['groupid'],
					'nickname': friends['name'],
					'remark': friends['remark'],
					'spacename': '',
					'age': 0,
					'birthday': '',
					'city': '',
					'img': friends['img'],
					'yellow': friends['yellow'],
					'online': friends['online'],
					'v6': friends['v6']}
			print 'insert id %s: ' % id + data['remark']
			self.operate_db_friends(db, 'qq_friends', data)
			id += 1
		self.write2file("friends.txt", str(friends['uin']))
		print '\ntotal friends: %s\ndone.' % id

	def get_friends_detail(self, qq, cookie, qq_num):
		s = qq.session
		s.cookies = cookie
		g_tk = str(qq.g_tk())
		url = 'https://h5.qzone.qq.com/proxy/domain/base.qzone.qq.com/cgi-bin/user/cgi_userinfo_get_all?uin=' + str(qq_num) + '&fupdate=1&outCharset=utf-8&g_tk=' + g_tk
		header = self.header
		r = s.get(url, headers = header)
		# r.content = r.content.replace('"Ⅰ', '')				#有些非主流的文字坑死人=_=#
		dict = self.data2json(r.content[10:-2].replace('\'', '').replace('\r\n', '').replace('\\', ''))
		if dict['code'] == 0:
			return dict['data']
		else:
			return ''

	def operate_db_friends(self, db, tablename, data):
		self.db = db

		create_tb_sql = 'CREATE TABLE IF NOT EXISTS %s\
			(id int primary key, \
			uin varchar(15), \
			sex int(2), \
			groupid int(2), \
			nickname varchar(40), \
			remark varchar(20), \
			spacename varchar(50), \
			age int(2), \
			birthday varchar(20), \
			city varchar(20), \
			img varchar(60), \
			yellow int(2), \
			online int(2), \
			v6 int(2)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4' % tablename		#change mysql encoding to support emoji
		db.Create_table(tablename, create_tb_sql)

		insert_data_sql = 'INSERT INTO %s values(%s, %s, %s, %s, "%s", "%s", "%s", %s, "%s", "%s", "%s", %s, %s, %s)' % \
			(tablename,
			data['id'],
			data['uin'],
			data['sex'],
			data['groupid'],
			data['nickname'],
			data['remark'],
			data['spacename'],
			data['age'],
			data['birthday'],
			data['city'],
			data['img'],
			data['yellow'],
			data['online'],
			data['v6'])
		# print insert_data_sql.encode('GB18030')
		db.Insert_data(tablename, insert_data_sql, data)

	def data2json(self, data):
		json_obj = json.loads(data.decode('utf-8'))
		return json_obj

	def write2file(self, filename, data):
		with open(filename, 'w') as f:
			f.write(data)
