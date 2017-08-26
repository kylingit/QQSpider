# -*- coding:utf-8 -*-

import pymysql
import warnings

warnings.filterwarnings("ignore")


class DB(object):
    """
    数据库相关模块
    """
    conn = None

    def __init__(self):
        try:
            self.conn = pymysql.connect("127.0.0.1", "root", "TooR", charset="utf8")
            self.cursor = self.conn.cursor()
            print('databases connected.')
        except:
            print('databases username or password wrong, exit.')

    def Create_db(self, dbname):
        cursor = self.cursor
        cursor.execute("SET NAMES utf8mb4")
        cursor.execute("SET CHARACTER SET utf8mb4")
        cursor.execute("SET character_set_connection = utf8mb4")
        # cursor.execute('DROP DATABASE IF EXISTS %s' % dbname)
        cursor.execute('CREATE DATABASE IF NOT EXISTS %s CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci' % dbname)        # change mysql encoding to support emoji
        self.conn.select_db(dbname)

    def Create_table(self, tablename, sql):
        cursor = self.cursor
        cursor.execute(sql)

    def Insert_data(self, tablename, sql, data):
        cursor = self.cursor
        cursor.execute(sql)
        self.conn.commit()

    def Update_data(self, tablename, sql, data):
        cursor = self.cursor
        cursor.execute(sql)
        self.conn.commit()

    def Query_data(self, tablename, sql):
        cursor = self.cursor
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

    def Delete_data(self, tablename, sql):
        cursor = self.cursor
        cursor.execute(sql)
        self.conn.commit()

    def Drop_table(self, tablename):
        cursor = self.cursor
        cursor.execute('DROP TABLE IF EXISTS %s' % tablename)

    def Drop_db(self, dbname):
        cursor = self.cursor
        cursor.execute('DROP DATABASE IF EXISTS %s' % dbname)

    def __del__(self):
        self.conn.close()
