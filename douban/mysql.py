import pymysql
from douban.config import *


class MySQL():
    def __init__(self, host=MYSQL_HOST, username=MYSQL_USER, password=MYSQL_PASSWORD, port=MYSQL_PORT,
                 database=MYSQL_DATABASE):
        """
        MySQL初始化
        :param host:
        :param username:
        :param password:
        :param port:
        :param database:
        """
        try:
            self.db = pymysql.connect(host, username, password, database, charset='utf8', port=port)
            self.cursor = self.db.cursor()
        except pymysql.MySQLError as e:
            print(e.args)
    
    def insert(self, table, data):
        """
        插入数据
        :param table:
        :param data:
        :return:
        """
        # keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql_query = 'insert into %s  values (%s)' % (table, values)
        try:
            self.cursor.execute(sql_query, data)
            self.db.commit()
        except pymysql.MySQLError as e:
            print(e.args)
            self.db.rollback()

    def repetition(self,movie_item):
        """检查重复"""
        sql = "SELECT `name` FROM movies WHERE name=%s limit 1"
        sqname = {}
        sqname['name'] = movie_item['name']
        rename = tuple(sqname.values())
        repetition = self.cursor.execute(sql, rename)
        return repetition

