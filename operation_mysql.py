import pymysql


class Mysql(object):
    def __init__(self):
        """连接数据库，获取conn"""
        self.mysql_host = "127.0.0.1"  # 数据库ip
        self.mysql_db = "tw"  # 数据库名称，要提前在mysql中创建好数据库
        self.mysql_user = "root"  # 数据库登录账号
        self.mysql_password = "123456"  # 数据库登录密码
        self.mysql_port = 3306  # 数据库端口号
        # self.sql = sql

        # 下面这个sql语句是用来创建mysql数据表的，用来记录注册账户信息
        # "CREATE TABLE id_info (id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(20), company_name VARCHAR(20),phone_number VARCHAR(20), mobile_number VARCHAR(20),key_products VARCHAR(20), country_id INT(3),email VARCHAR(20), password VARCHAR(20),messenger_type VARCHAR(20), messenger_id VARCHAR(20));"
        # 下面这个sql语句是用来创建商品类目表的，记录网站上提供的商品分类
        # CREATE TABLE ind_info (id INT(10),name VARCHAR(20));



        self.conn = pymysql.connect(host=self.mysql_host, port=self.mysql_port, user=self.mysql_user, password=self.mysql_password,
                               db=self.mysql_db, charset='UTF8MB4')
        self.cur = self.conn.cursor()


    def get_all(self, sql):

        try:
            self.cur.execute(sql)
        except Exception as e:
            print(e)
        result = self.cur.fetchall()
        return result   # 结果是元组

    def insert_into(self, sql, args):

        try:
            self.cur.execute(sql, args)
        except Exception as e:
            print(e)
            self.conn.rollback()
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()