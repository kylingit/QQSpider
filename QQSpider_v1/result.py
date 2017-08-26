#-*- coding:utf-8 -*-

from db import db
from handle import handle

if __name__ == '__main__':
	db = db.DB()
	db.Create_db('result')

	handle = handle.Handle_data()
	for dbname in handle.get_user_db(db, 'SCHEMATA'):
		db.conn.select_db(dbname[0])
		db.cursor.execute('SHOW TABLES')
		for i in db.cursor.fetchall():
			if 'qq_moods' in i[0]:
				data = handle.get_moods_data(db, dbname[0], 'qq_moods')
				handle.operate_moods_db(db, 'result', 'moods_result', data)
				break