# -*- coding:utf-8 -*-
import codecs


class Status(object):
    """
    保存爬取的状态，便于意外退出后恢复而不是从头开始
    """
    def __init__(self):
        pass
        # self.crawlerid = 0
        # self.moodid = 0
        # self.msgid = 0

    def create_status_db(self, db, dbname):
        self.db = db
        db.Create_db(dbname)

    def save_mood_status(self, db, tablename, target_qq, moodstatus):
        self.db = db
        create_tb_sql = 'CREATE TABLE IF NOT EXISTS %s ( \
            qq_num varchar(15), \
            moodTid varchar(30), \
            is_last_mood int(2), \
            moodPos int(10), \
            moodId int(10), \
            moodcmtId int(10), \
            moodlikeId int(10) \
        )' % tablename
        db.Create_table(tablename, create_tb_sql)

        insert_data_sql = 'INSERT INTO %s values("%s", "%s", %s, %s, %s, %s, %s)' % (
            tablename,
            target_qq,
            moodstatus['moodTid'],
            moodstatus['is_last_mood'],
            moodstatus['moodPos'],
            moodstatus['moodId'],
            moodstatus['moodcmtId'],
            moodstatus['moodlikeId']
        )

        db.Insert_data(tablename, insert_data_sql, moodstatus)
        # self.moodid += 1

    def update_mood_status(self, db, tablename, target_qq, moodstatus):
        self.db = db
        update_data_sql = 'UPDATE %s SET moodTid="%s", is_last_mood=%s, moodPos=%s, moodId=%s, moodcmtId=%s, moodlikeId=%s WHERE qq_num="%s"' % (
            tablename,
            moodstatus['moodTid'],
            moodstatus['is_last_mood'],
            moodstatus['moodPos'] - 10,
            moodstatus['moodId'],
            moodstatus['moodcmtId'],
            moodstatus['moodlikeId'],
            target_qq
        )

        db.Update_data(tablename, update_data_sql, moodstatus)

    def delete_mood(self, db, tablename, data, value):
        self.db = db
        delete_mood_sql = 'DELETE FROM %s WHERE %s=%s' % (tablename, data, value)
        db.Delete_data(tablename, tablename, delete_mood_sql)

    def save_msg_status(self, db, tablename, target_qq, msgdata):
        """保存留言状态 未完善"""
        self.db = db
        create_tb_sql = 'CREATE TABLE IF NOT EXISTS %s ( \
            id int primary key, \
            qq_num varchar(15), \
            messagesid varchar(15), \
            is_last_msg int(2), \
            msgPos int(10), \
            msgId int(10), \
            msgreplyId int(10) \
        )' % tablename

        db.Create_table(tablename, create_tb_sql)

        insert_data_sql = 'INSERT INTO %s values(%s, "%s", "%s", %s, %s, %s, %s)' % (
            tablename,
            self.msgid,
            target_qq,
            msgdata['messagesid'],
            msgdata['is_last_msg'],
            msgdata['msgPos'],
            msgdata['msgId'],
            msgdata['msgreplyId']
        )

        # db.Insert_data(tablename, insert_data_sql, data)
        # self.msgid += 1

    def load_mood_status(self, db, tablename, target_qq):
        self.db = db
        query_status_sql = 'SELECT moodTid, is_last_mood, moodPos, moodId, moodcmtId, moodlikeId FROM %s WHERE qq_num=%s' % (tablename, target_qq)
        statusdict = {}
        for status in db.Query_data(tablename, query_status_sql):
            if status[0] == '' and status[1] != 1:
                # print('loading status...')
                statusdict = {
                    "moodTid": '', "is_last_mood": 0, "moodPos": 0,
                    "moodId": 0, "moodcmtId": 0, "moodlikeId": 0
                }

            elif status[0] != '' and status[1] == 0:
                print(u'检测到该 qq 号上回还没有爬取完毕，继续爬取...')
                print(u'清除可能冗余的数据...')
                statusdict = {
                    "moodTid": status[0], "is_last_mood": 0, "moodPos": status[2],
                    "moodId": status[3], "moodcmtId": status[4], "moodlikeId": status[5]
                }
                # print(statusdict)

                get_moodid_sql = 'SELECT id FROM qq_moods WHERE moodid="%s"' % status[0]
                # print(get_moodid_sql)
                moodid = db.Query_data('qq_moods', get_moodid_sql)
                delete_mood_sql = 'DELETE FROM qq_moods WHERE id>%s' % moodid[0]
                print(delete_mood_sql)
                db.Delete_data('qq_moods', delete_mood_sql)

                get_moodreplyid_sql = 'SELECT id FROM qq_moods_reply WHERE moodid="%s" order by id DESC limit 1' % status[0]
                # print(get_moodreplyid_sql)
                moodreplyid = db.Query_data('qq_moods_reply', get_moodreplyid_sql)
                if moodreplyid != ():
                    delete_moodreply_sql = 'DELETE FROM qq_moods_reply WHERE id>%s' % moodreplyid[0]
                    print(delete_moodreply_sql)
                    db.Delete_data('qq_moods_reply', delete_moodreply_sql)
                    statusdict['moodcmtId'] = moodreplyid[0][0] + 1
                else:
                    delete_moodreply_sql = 'DELETE FROM qq_moods_reply WHERE id>=%s' % status[4]
                    print(delete_moodreply_sql)
                    db.Delete_data('qq_moods_reply', delete_moodreply_sql)

            elif status[1] == 1:
                print(target_qq + u': 该 qq 的说说数据已爬取完毕.')
                log = codecs.open('log.txt', 'a', 'utf-8')
                log.write('\n' + target_qq + u': 爬取完毕.\n')

        return statusdict
