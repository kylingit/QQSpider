# -*- coding:utf-8 -*-
import json
import time
import random
from util import util


class Get_messages(object):
    """
    获取留言信息和回复信息
    """
    def __init__(self):
        self.messageId = 0
        self.replyId = 0

    def get_messages(self, qq, target_qq, cookie, db):
        """获取所有留言"""
        start = 0
        s = qq.session
        s.cookies = cookie
        g_tk = str(qq.g_tk())

        header = util.headers
        url = 'https://h5.qzone.qq.com/proxy/domain/base.qzone.qq.com/cgi-bin/user/cgi_userinfo_get_all?uin=' + target_qq + '&fupdate=1&g_tk=' + g_tk
        # print(url)
        r = s.get(url, headers=header)

        if r.content.decode('utf-8').find(u'您无权访问') > 0:
            print(u'空间主人设置了访问权限，您无法进行操作')
        else:
            while True:
                url = 'https://h5.qzone.qq.com/proxy/domain/m.qzone.qq.com/cgi-bin/new/get_msgb?uin=' \
                    + qq.user + '&hostUin=' + target_qq + '&start=' + str(start) \
                    + '&num=10&format=jsonp&inCharset=utf-8&outCharset=utf-8&g_tk=' + g_tk

                r = s.get(url, headers=header)
                dict = self.data2json(r.content[10:-2])
                if start < dict['data']['total'] - 1:                # get 10 items at a time
                    print(str(start) + '-' + str(start + 10) + ':')
                    start = start + 10
                else:
                    break
                time.sleep(random.random())

                self.operate_db_message(db, 'qq_messages', dict)
                self.operate_db_reply(db, 'qq_messages_reply', dict)

            print('\nmessages total count: %s' % self.messageId)
            print('reply total count: %s \n\ndone.' % self.replyId)

    def operate_db_message(self, db, tablename, data):
        """留言信息入库"""
        self.db = db

        create_tb_sql = 'CREATE TABLE IF NOT EXISTS %s ( \
            id int primary key, \
            msgid varchar(15), \
            uin varchar(15), \
            nickname varchar(50), \
            secret int(2), \
            bmp varchar(20), \
            pubtime varchar(20), \
            modifytime varchar(20), \
            effect char(10), \
            type int(2), \
            capacity varchar(10), \
            ubbContent TEXT, \
            replyFlag int(2))' % tablename
        db.Create_table(tablename, create_tb_sql)

        for item in data['data']['commentList']:
            i = {'replyFlag': 0}                               # 是否有回复
            if item['secret'] == 0:                            # 私密留言
                for i in item['replyList']:
                    if item['replyList'] == []:                # set replyFlag=1 when replyList exsit
                        i['replyFlag'] = 0
                    else:
                        i['replyFlag'] = 1

                insert_data_sql = 'INSERT INTO %s values(%s, "%s", "%s", "%s", %s, "%s", "%s", "%s", "%s", %s, "%s", "%s", %s)' % (
                    tablename,
                    self.messageId,
                    item['id'],
                    item['uin'],
                    item['nickname'].replace('"', '').replace('[em]', '').replace('[/em]', ''),
                    item['secret'],
                    item['bmp'],
                    item['pubtime'],
                    item['modifytime'],
                    item['effect'],
                    item['type'],
                    item['capacity'],
                    item['ubbContent'].replace('"', ''),
                    i['replyFlag'])
            else:
                insert_data_sql = 'INSERT INTO %s values(%s, "%s", "%s", "%s", %s, "%s", "%s", "%s", "%s", %s, "%s", "%s", %s)' % (
                    tablename,
                    self.messageId,
                    item['id'],
                    '',
                    u'私密留言',
                    item['secret'],
                    item['bmp'],
                    item['pubtime'],
                    item['modifytime'],
                    item['effect'],
                    item['type'],
                    '',
                    u'私密留言',
                    0)

            insert_data_sql = insert_data_sql.strip().replace(';', '')\
                .replace("'", '').replace('%', '').replace('\\', '')\
                .replace('\r', '').replace('\t', '').replace('\n', '')

            db.Insert_data(tablename, insert_data_sql, data)
            print('get messageId %s: ' % self.messageId + str(item['id']))

            self.messageId += 1

    def operate_db_reply(self, db, tablename, data):
        """留言回复信息入库"""
        self.db = db
        create_tb_sql = 'CREATE TABLE IF NOT EXISTS %s ( \
            id int primary key, \
            msgid varchar(15), \
            replycount char(4), \
            uin varchar(15), \
            nickname varchar(50), \
            pubtime varchar(20), \
            content TEXT \
        )' % tablename

        db.Create_table(tablename, create_tb_sql)
        for item in data['data']['commentList']:
            if 'replyList' in item and item['replyList'] != []:
                replyCount = str(len(item['replyList']))
                for reply in item['replyList']:
                    pubtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reply['time']))

                    insert_data_sql = 'INSERT INTO %s values(%s, "%s", "%s", "%s", "%s", "%s", "%s")' % (
                        tablename,
                        self.replyId,
                        item['id'],
                        replyCount,
                        reply['uin'],
                        reply['nick'].replace('"', '').replace('[em]', '').replace('[/em]', ''),
                        pubtime,
                        reply['content']
                    )

                    db.Insert_data(tablename, insert_data_sql, data)
                    replyCount = ''
                    print('get replyId %s: ' % self.replyId + str(item['uin']))

                    self.replyId += 1

    def data2json(self, data):
        json_obj = json.loads(data.decode('utf-8'))
        return json_obj

    def write2file(self, filename, data):
        with open(filename, 'w+') as f:
            f.write(data)
