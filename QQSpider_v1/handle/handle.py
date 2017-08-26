#-*- coding:utf-8 -*-

import MySQLdb
from datetime import datetime
# from db import db

class Handle_data(object):
	def __init__(self):
		self.id = 0
		# pass

	def get_user_db(self, db, tablename):
		self.db = db
		db.conn.select_db('information_schema')
		get_db_sql = 'SELECT SCHEMA_NAME FROM SCHEMATA WHERE SCHEMA_NAME LIKE \'db%\''
		# print get_db_sql
		return db.Query_data(tablename, get_db_sql)

	def get_moods_data(self, db, dbname, tablename):
		self.db = db
		data = {}
		db.conn.select_db(dbname)

		data['uin'] = dbname[2:]

		get_remark_sql = 'SELECT remark FROM db12345678.qq_friends WHERE uin = %s' % data['uin']
		for remark in db.Query_data(tablename, get_remark_sql):
			data['remark'] = remark[0]

		get_count_sql = 'SELECT COUNT(id), SUM(cmtnum), MAX(cmtnum), ROUND(AVG(cmtnum),2) FROM %s' % tablename
		for count in db.Query_data(tablename, get_count_sql):
			data['moods_count'] = count[0]
			data['moods_cmtcount'] = count[1]
			data['max_cmtcount'] = count[2]
			data['avg_cmtcount'] = count[3]

		get_like_count_sql = 'SELECT SUM(CAST(SUBSTRING(likecount, 1) AS UNSIGNED)), MAX(CAST(SUBSTRING(likecount, 1) AS UNSIGNED)), \
			ROUND(AVG(CAST(SUBSTRING(likecount, 1) AS UNSIGNED)), 2) FROM qq_moods_like WHERE likecount != \'\''
		# print get_like_count_sql
		try:
			for count in db.Query_data('qq_moods_like', get_like_count_sql):
				data['moods_likecount'] = count[0]
				data['max_likecount'] = count[1]
				data['avg_likecount'] = count[2]
		except:
			data['moods_likecount'] = 0
			data['max_likecount'] = 0
			data['avg_likecount'] = 0
			pass


		get_time_sql = 'SELECT pubtime FROM %s ORDER BY id DESC LIMIT 1' % tablename
		for time in db.Query_data(tablename, get_time_sql):
			data['earliest_pubtime'] = time[0]

		get_time_sql = 'SELECT pubtime FROM %s WHERE id = 0' % tablename
		for time in db.Query_data(tablename, get_time_sql):
			data['latest_pubtime'] = time[0]

		earliest_pubtime = datetime.strptime(data['earliest_pubtime'][:10], '%Y-%m-%d')
		latest_pubtime = datetime.strptime(data['latest_pubtime'][:10], '%Y-%m-%d')
		time_span = (latest_pubtime - earliest_pubtime).days
		data['time_span'] = time_span

		get_average_sql = 'SELECT AVG(t.count) FROM(SELECT DATE_FORMAT(pubtime,\'%Y%m%d\') days, count(*) count FROM qq_moods GROUP BY days) t;'
		for average in db.Query_data(tablename, get_average_sql):
			data['avg_mdcount_day'] = average[0]

		get_average_sql = 'SELECT AVG(t.count) FROM(SELECT DATE_FORMAT(pubtime,\'%Y_%u\') weeks, count(*) count FROM qq_moods GROUP BY weeks) t;'
		for average in db.Query_data(tablename, get_average_sql):
			data['avg_mdcount_week'] = average[0]

		get_average_sql = 'SELECT AVG(t.count) FROM(SELECT DATE_FORMAT(pubtime,\'%Y%m\') months, count(*) count FROM qq_moods GROUP BY months) t;'
		for average in db.Query_data(tablename, get_average_sql):
			data['avg_mdcount_month'] = average[0]

		get_average_sql = 'SELECT AVG(t.count) FROM(SELECT FLOOR((DATE_FORMAT(pubtime, \'%m\')+2)/3) quarters, count(*) count FROM qq_moods GROUP BY quarters) t;'
		for average in db.Query_data(tablename, get_average_sql):
			data['avg_mdcount_quarter'] = average[0]

		get_average_sql = 'SELECT AVG(t.count) FROM(SELECT DATE_FORMAT(pubtime,\'%Y\') years, count(*) count FROM qq_moods GROUP BY years) t;'
		for average in db.Query_data(tablename, get_average_sql):
			data['avg_mdcount_year'] = average[0]

		return data



	def operate_moods_db(self, db, dbname, tablename, data):
		self.db = db
		db.conn.select_db(dbname)

		create_tb_sql = 'CREATE TABLE IF NOT EXISTS %s\
			(id int primary key, \
			uin varchar(15), \
			remark varchar(20), \
			moods_count int(4), \
			moods_cmtcount int(4), \
			max_cmtcount int(4),\
			avg_cmtcount float(5,2), \
			moods_likecount int(4),\
			max_likecount int(4),\
			avg_likecount float(5,2), \
			earliest_pubtime varchar(20), \
			latest_pubtime varchar(20), \
			time_span varchar(10), \
			avg_mdcount_day float(5,2), \
			avg_mdcount_week float(5,2), \
			avg_mdcount_month float(5,2), \
			avg_mdcount_quarter float(5,2), \
			avg_mdcount_year float(5,2) \
			) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4' % tablename

		db.Create_table(tablename, create_tb_sql)

		insert_data_sql = 'INSERT INTO %s values(%s, "%s", "%s", %s, %s, %s, %s, %s, %s, %s, "%s", "%s", "%s", %s, %s, %s, %s, %s)' % \
			(tablename,
			self.id,
			data['uin'],
			data['remark'],
			data['moods_count'],
			data['moods_cmtcount'],
			data['max_cmtcount'],
			data['avg_cmtcount'],
			data['moods_likecount'],
			data['max_likecount'],
			data['avg_likecount'],
			data['earliest_pubtime'],
			data['latest_pubtime'],
			data['time_span'],
			data['avg_mdcount_day'],
			data['avg_mdcount_week'],
			data['avg_mdcount_month'],
			data['avg_mdcount_quarter'],
			data['avg_mdcount_year']
			)
		# print insert_data_sql
		db.Insert_data(tablename, insert_data_sql, data)
		self.id += 1

		print 'insert id %s: %s' % (self.id, data['remark'])
