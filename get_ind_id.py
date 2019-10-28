import html
from threading import Thread
import requests
import re
import json
from queue import Queue
import time
from operation_mysql import Mysql
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class IndId(object):
    """这个脚本用来获取所有类目ID的，运行一次就好了"""
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
        self.session = requests.session()
        self.login_get_url = 'https://www.tradewheel.com/login/'
        self.login_post_url = 'https://www.tradewheel.com/ajax/login'
        self.url_queue = Queue()
        self.ind_queue = Queue()
        # self.proxies = {"https": "http://116.62.228.199:3128"}

    def get(self):
        """为后面的登录post请求"""
        res = self.session.get(url=self.login_get_url, headers=self.headers, verify=False).text
        with open('./a.html', 'w', encoding='utf-8')as f:
            f.write(res)
        # print(res)
        token = re.findall(r'name="_token" type="hidden" value="(.*?)"', res)[0]
        return token

    def post(self, token):
        """根据需要登录的email，查询好对应的密码，构建参数，发起post请求，实现登录"""
        data = {
            '_token': token,
            'email': '44211@qq.com',
            'password': '123',
        }
        res = self.session.post(url=self.login_post_url, headers=self.headers, data=data, verify=False)
        # print(res.url)
        if res.url == 'https://www.tradewheel.com/member/dashboard':
            return True
        else:
            return False

    def get_ind1_id(self, result):
        """获取1级类目"""
        if result:
            print('登陆成功，开始采集类目信息')
            url = 'https://www.tradewheel.com/member/products/add/'
            res = self.session.get(url=url, headers=self.headers, verify=False).text

            ind_list = re.findall(r'<option value="(\d{1,2})">(.*?)</option>', res)[0:-2]
            for i in ind_list:
                ind_dict = {}
                ind_dict['id'] = i[0]
                ind_dict['value'] = html.unescape(i[1])
                print(ind_dict)
                self.ind_queue.put(ind_dict)

    def make_url(self):
        url = 'https://www.tradewheel.com/member/get_industries?parent_id={}'
        for i in range(1, 41):
            self.url_queue.put(url.format(i))

    def parse(self):
        while True:
            url = self.url_queue.get()
            # time.sleep(1)
            print(url)
            response = self.session.get(url=url, headers=self.headers, verify=False).text
            try:
                response = json.loads(response)
            except Exception as e:
                print(e)
                print(response)
                continue

            if len(response) > 0:
                for item, value in response.items():
                    ind2_dict = {}
                    ind2_dict['id'] = item
                    value = html.unescape(value)
                    ind2_dict['value'] = value
                    self.ind_queue.put(ind2_dict)
                    if int(item) < 800:
                        url = 'https://www.tradewheel.com/member/get_industries?parent_id=%s' % item
                        self.url_queue.put(url)
                    # print(url)
                    print(ind2_dict)
            self.url_queue.task_done()

    def insert(self):
        """把分类信息数据插入数据库"""
        mysql_db = Mysql()
        while True:
            ind_dict = self.ind_queue.get()
            sql = 'replace into ind_info (id,name) value (%s, %s)'
            args = (ind_dict['id'], ind_dict['value'])
            mysql_db.insert_into(sql, args)
            self.ind_queue.task_done()
        mysql_db.close()

    def run(self):
        token = self.get()
        result = self.post(token)
        self.get_ind1_id(result)
        self.make_url()
        # self.parse()
        for i in range(1):
            t1 = Thread(target=self.parse)
            t1.setDaemon(True)
            t1.start()
        # for i in range(5):
        #     t2 = Thread(target=self.insert)
        #     t2.setDaemon(True)
        #     t2.start()
        self.url_queue.join()
        self.ind_queue.join()


if __name__ == '__main__':
    ind_id = IndId()
    ind_id.run()