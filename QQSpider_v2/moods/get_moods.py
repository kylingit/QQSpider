# -*- coding:utf-8 -*-

import json
import time
import random
import codecs
from util import util
from status import status


class Get_moods(object):
    """
    说说数据和回复数据
    """
    def __init__(self):
        self.header = util.headers
        self.cookie = util.cookie
        self.moodstatus = {"moodTid": '', "is_last_mood": 0, "moodPos": 0, "moodId": 0, "moodcmtId": 0, "moodlikeId": 0}
        self.mood_status = status.Status()

    def get_moods(self, qq, target_qq, cookie, db):
        """获取所有说说和回复数据"""
        s = qq.session
        s.cookies = cookie
        g_tk = str(qq.g_tk())

        header = self.header
        url = 'https://h5.qzone.qq.com/proxy/domain/base.qzone.qq.com/cgi-bin/user/cgi_userinfo_get_all?uin=' + target_qq + '&fupdate=1&g_tk=' + g_tk
        r = s.get(url, headers=header)

        if r.content.decode('utf-8').find(u'您无权访问') > 0:
            print(u'空间主人设置了访问权限，您无法进行操作.\n')
            db.Drop_db('db' + target_qq)
            log = codecs.open('log.txt', 'a', 'utf-8')
            log.write('\n' + target_qq + ': cannot access.\n')
        else:
            try:
                while True:
                    url = 'https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?uin=' + \
                        target_qq + '&pos=' + str(self.moodstatus['moodPos']) + '&num=10&format=jsonp&g_tk=' + g_tk
                    # print(url)
                    r = s.get(url, headers=header)
                    r.content.strip().decode().replace('\n', '')

                    dict = self.data2json(r.content[10:-2])
                    if self.moodstatus['moodPos'] < dict['usrinfo']['msgnum'] - 1:                # get 10 items at a time
                        self.moodstatus['moodPos'] += 10
                        print('current qq: %s, current pos: %s' % (target_qq, str(self.moodstatus['moodPos'])))
                    else:
                        break

                    if dict['msglist'] is None:
                        print(u'\n之前动态被封存，无法获取.')
                        log = codecs.open('log.txt', 'a', 'utf-8')
                        log.write('\n' + target_qq + u': 之前动态被封存，无法获取.')
                        self.moodstatus['is_last_mood'] = 1
                        break

                    self.mood_status.update_mood_status(db, 'mood_status', target_qq, self.moodstatus)              # 保存当前爬取的状态
                    print(self.moodstatus)

                    for item in dict['msglist']:
                        print('get moodId: %s, moods tid: %s' % (self.moodstatus['moodId'], item['tid']))
                        url = 'https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msgdetail_v6?uin=' + \
                            target_qq + '&tid=' + item['tid'] + '&format=jsonp&g_tk=' + g_tk
                        # print(url)
                        r = s.get(url, headers=header)

                        r.content.strip().decode().replace('\n', '').replace('\\', '')
                        data = self.data2json(r.content[10:-2])
                        time.sleep(random.random())

                        self.moodstatus['moodTid'] = item['tid']                               # 更新状态
                        self.operate_db_moods(db, 'qq_moods', data)                            # get moods details

                        if 'commentlist' in item.keys() and item['commentlist'] is not None:
                            self.operate_db_moods_reply(db, 'qq_moods_reply', data)            # get moods reply
                        # self.get_moods_like(qq, target_qq, cookie, item['tid'], db)            # get moods like 注意爬取频率过高会被禁止访问

            except Exception as e:                  # save status
                print('have a error!!!')
                print(repr(e), e)
                # log = codecs.open('log.txt', 'a', 'utf-8')
                # log.write('\nerror: ' + target_qq + ':' + repr(e) + e.decode() + '\n')
            else:
                self.moodstatus['is_last_mood'] = 1
                self.mood_status.update_mood_status(db, 'mood_status', target_qq, self.moodstatus)

                print('\ncurrent qq: %s' % target_qq)
                print('moods total count: %s' % str(self.moodstatus['moodId']))
                print('moods comment total count: %s' % str(self.moodstatus['moodcmtId']))
                print('moods like total count: %s\n\ndone.\n' % str(self.moodstatus['moodlikeId']))

                log = codecs.open('log.txt', 'a', 'utf-8')
                log.write(
                    '\ncurrent qq: ' + target_qq + ' moods total count: ' +
                    str(self.moodstatus['moodId']) + ' moods comment total count: ' +
                    str(self.moodstatus['moodcmtId']) + ' moods like total count: ' +
                    str(self.moodstatus['moodlikeId']) + '\n'
                )

    def get_moods_like(self, qq, target_qq, cookie, moodid, db):
        """说说点赞数据 注意点赞接口访问频率过高会导致 403"""
        s = qq.session
        s.cookies = cookie
        g_tk = str(qq.g_tk())

        header = self.header
        header['Upgrade-Insecure-Requests'] = '1'               # 点赞接口请求头含有额外字段
        unikey = 'http://user.qzone.qq.com/' + target_qq + '/mood/' + moodid
        url = 'https://h5.qzone.qq.com/proxy/domain/users.qzone.qq.com/cgi-bin/likes/get_like_list_app?uin=' + \
            qq.user + '&unikey=' + unikey + '&begin_uin=0&query_count=60&if_first_page=1&g_tk=' + g_tk
        # print(url)
        r = s.get(url, headers=header)

        if r.status_code != 403:
            dict = self.data2json(r.content[10:-3].strip().replace('\n', '').replace('\\', '').replace('"data":{', '"data":[{').replace('}}', '}]}'))
            if dict['data'] != '':
                for item in dict['data']:
                    if item['total_number'] != 0:
                        i = 0
                        for data in item['like_uin_info']:
                            print('get moodlikeId: ' + str(self.moodstatus['moodlikeId']))
                            if i == 0:
                                self.operate_db_moods_like(db, 'qq_moods_like', moodid, str(item['total_number']), data)
                            else:
                                self.operate_db_moods_like(db, 'qq_moods_like', moodid, '', data)
                            i += 1
        else:
            pass

    def operate_db_moods(self, db, tablename, data):
        """说说数据入库"""
        self.db = db

        create_tb_sql = 'CREATE TABLE IF NOT EXISTS %s ( \
            id int primary key, \
            moodid varchar(30), \
            uin varchar(15), \
            nickname varchar(50), \
            secret int(2), \
            pubtime varchar(20), \
            phone varchar(30), \
            content TEXT, \
            pictotal int(4), \
            cmtnum int(4), \
            fwdnum int(4), \
            locate varchar(50), \
            position varchar(50), \
            pos_x varchar(20), \
            pos_y varchar(20) \
        )' % tablename

        db.Create_table(tablename, create_tb_sql)

        pubtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['created_time']))

        if data['content'].strip() == '' and 'rt_con' in data:
            try:
                data['content'] = data['rt_con']['conlist'][0]['con'].replace('"', '')
            except(IndexError):
                data['content'] = data['rt_con']['conlist'][1]['con'].replace('"', '')
            except(KeyError):
                data['content'] = data['rt_con']['content'].replace('"', '')
            except(TypeError):
                try:
                    data['content'] = data['video'][0]['url3'].replace('"', '')
                except:
                    data['content'] = ''

        if data['content'] == '':                   # 说说中的图片信息
            if 'pic' in data.keys() and data['pic'] != '':
                data['content'] = data['pic'][0]['url2']
            else:
                data['content'] = ''

        if 'pictotal' in data.keys():
            pictotal = data['pictotal']
        else:
            pictotal = 0

        insert_data_sql = 'INSERT INTO %s values(%s, "%s", "%s", "%s", %s, "%s", "%s", "%s", %s, %s, %s, "%s", "%s", "%s", "%s")' % (
            tablename,
            self.moodstatus['moodId'],
            data['tid'],
            data['usrinfo']['uin'],
            data['usrinfo']['name'].replace('"', '').replace('\n', '').replace('\\', '').replace('[em]', '').replace('[/em]', ''),
            data['secret'],
            pubtime,
            data['source_name'],
            data['content'].replace('"', '').replace('\n', '').replace('\\', ''),
            pictotal,
            data['cmtnum'],
            data['fwdnum'],
            data['lbs']['name'],
            data['lbs']['idname'],
            data['lbs']['pos_x'],
            data['lbs']['pos_y']
        )

        # print(insert_data_sql.encode('GB18030')))
        db.Insert_data(tablename, insert_data_sql, data)

        self.moodstatus['moodId'] += 1

    def operate_db_moods_reply(self, db, tablename, data):
        """说说回复数据入库"""
        self.db = db
        create_tb_sql = 'CREATE TABLE IF NOT EXISTS %s\
            (id int primary key, \
            moodid varchar(30), \
            cmtuin varchar(15), \
            cmtnickname varchar(80), \
            cmtcount varchar(4), \
            cmtpubtime varchar(20), \
            comtcontent TEXT, \
            replycount varchar(4), \
            rpypubtime varchar(20), \
            replycontent TEXT \
        )' % tablename
        db.Create_table(tablename, create_tb_sql)

        for item in data['commentlist']:
            if len(str(item['owner']['uin'])) >= 15:                    # 早期时候转发的说说不显示转发者 qq 号，而是说说的 id，由于过长故舍去
                item['owner']['uin'] = ''
            insert_data_sql = 'INSERT INTO %s values(%s, "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % (
                tablename,
                self.moodstatus['moodcmtId'],
                data['tid'],
                item['owner']['uin'],
                item['owner']['name'].replace('\n', '').replace('"', '').replace('[em]', '').replace('[/em]', '').replace('\\', ''),
                str(data['cmtnum']),
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['create_time'])),
                item['content'].replace('"', '').replace('\n', '').replace('\\', ''),
                str(len(item['list_3'])) if 'list_3' in item.keys() else '',
                '',
                ''
            )
            db.Insert_data(tablename, insert_data_sql, data)
            self.moodstatus['moodcmtId'] += 1

            if 'list_3' in item.keys():                                 # 回复嵌套结构额外处理
                for reply in item['list_3']:
                    insert_data_sql = 'INSERT INTO %s values(%s, "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % (
                        tablename,
                        self.moodstatus['moodcmtId'],
                        data['tid'],
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reply['create_time'])),
                        reply['content'].replace('"', '').replace('\n', '').replace('\\', '')
                    )
                    db.Insert_data(tablename, insert_data_sql, data)
                    self.moodstatus['moodcmtId'] += 1

            print('get moodcmtId: %s' % self.moodstatus['moodcmtId'])

    def operate_db_moods_like(self, db, tablename, moodid, likecount, data):
        """说说点赞数据入库"""
        self.db = db

        create_tb_sql = 'CREATE TABLE IF NOT EXISTS %s (\
            id int primary key, \
            moodid varchar(30), \
            likecount  varchar(6), \
            uin varchar(15), \
            nickname varchar(50), \
            gender varchar(4), \
            constellation varchar(10), \
            addr varchar(10), \
            if_qq_friend int(2), \
            if_special_care int(2) \
        )' % tablename
        db.Create_table(tablename, create_tb_sql)

        insert_data_sql = 'INSERT INTO %s values(%s, "%s", "%s", "%s", "%s", "%s", "%s", "%s", %s, %s)' % (
            tablename,
            self.moodstatus['moodlikeId'],
            moodid,
            likecount,
            data['fuin'],
            data['nick'],
            data['gender'],
            data['constellation'],
            data['addr'],
            data['if_qq_friend'],
            data['if_special_care']
        )

        db.Insert_data(tablename, insert_data_sql, data)
        # print('get likeId: ' + str(self.moodstatus['moodlikeId']))
        self.moodstatus['moodlikeId'] += 1

    def data2json(self, data):
        json_obj = json.loads(data.decode('utf-8'))
        return json_obj
