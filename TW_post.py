import requests
import sys
import re
import json
import time
from lxml import etree
from operation_mysql import Mysql
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}


class Register(object):
    """实现注册账号，并将注册成功的账户存入MySQL。实例化的时候需传入注册需要的数据reg_data,字典形式"""
    def __init__(self, reg_data):
        self.reg_data = reg_data
        self.session = requests.session()
        self.get_url = 'https://www.tradewheel.com/register-free'
        self.post_url = 'https://www.tradewheel.com/ajax/register-free'

    def get(self):
        """先用session访问，获取cookie，并保持回话状态，同时也要获取一下token"""
        res = self.session.get(url=self.get_url, headers=headers).content.decode()
        token = re.findall(r'name="_token" type="hidden" value="(.*?)"', res)[0]
        # with open('./b.html', 'w', encoding='utf-8') as f:
        #     f.write(res)
        return token

    def post(self, token):
        """以之前的session实例发起post请求"""
        # 不需要人工提供data的内容
        form_data = {
            '_token': token,
            'source': 'organic',
            'widget_source': 'register_page',
            'referrer_url': '',
            'page_url': 'https://www.tradewheel.com/register-free',
            'landing_url': 'https://www.tradewheel.com/register-free',
            'type': 'seller',
        }
        data = dict(form_data, **self.reg_data)  # 合并字典，形成post需要的全部的data内容
        res = self.session.post(url=self.post_url, headers=headers, data=data, verify=False)
        res = res.text
        res = json.loads(res)
        result = res['error']
        if len(result) == 0:
            result = res['message']
        return result

    def save_info(self, result):
        """将注册成功的账号信息插入mysql"""
        if result == 'You have registered succesfullly!.':
            print(self.reg_data['email'], '注册成功')
            # 构建sql语句
            sql = 'insert into id_info (name,company_name,phone_number,mobile_number,key_products,country_id,email,password,messenger_type,messenger_id)' \
                  'value (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            # 构建插入的值
            args = (self.reg_data['name'],
                    self.reg_data['company_name'],
                    self.reg_data['phone_number'],
                    self.reg_data['mobile_number'],
                    self.reg_data['key_products'],
                    self.reg_data['country_id'],
                    self.reg_data['email'],
                    self.reg_data['password'],
                    self.reg_data['messenger_type'],
                    self.reg_data['messenger_id'],
                    )
            # 实例化操作数据库的类，调用相应方法插入数据
            mysql_db = Mysql()
            mysql_db.insert_into(sql, args)
            mysql_db.close()

    def run(self):
        token = self.get()
        result = self.post(token)
        self.save_info(result)


class ReleaseGoods(object):
    """实现登录账号并发布商品功能"""

    def __init__(self, id_email, goods_data, files):
        self.session = requests.session()
        self.login_get_url = 'https://www.tradewheel.com/login/'
        self.login_post_url = 'https://www.tradewheel.com/ajax/login'
        self.add_get_url = 'https://www.tradewheel.com/member/products/add'
        self.add_post_url = 'https://www.tradewheel.com/member/products/store'
        self.id_email = id_email
        self.goods_data = goods_data
        self.files = files

    def get(self, url):
        """为后面的登录post请求"""
        res = self.session.get(url=url, headers=headers).content.decode()
        token = re.findall(r'name="_token" type="hidden" value="(.*?)"', res)[0]
        # print(token)
        return token

    def post(self, token):
        """根据需要登录的email，查询好对应的密码，构建参数，发起post请求，实现登录"""
        sql = "select password from id_info where email='%s';" % self.id_email
        mysql_db = Mysql()
        pwd = mysql_db.get_all(sql)[0][0]
        mysql_db.close()
        # print(pwd)
        data = {
            '_token': token,
            'email': self.id_email,
            'password': pwd,
        }
        res = self.session.post(url=self.login_post_url, headers=headers, data=data, verify=False)
        # print(res.url)
        if res.url == 'https://www.tradewheel.com/member/dashboard':
            print('登录成功')
            return True
        else:
            return False

    def get_group(self):
        url = 'https://www.tradewheel.com/member/products/groups/'
        response = self.session.get(url=url, headers=headers).text
        res_html = etree.HTML(response)
        tr_list = res_html.xpath('//div[@class="col"]/table/tbody/tr')
        group_list = []
        # print(len(tr_list))
        for tr in tr_list:
            group = {}
            try:
                group['name'] = tr.xpath('./td[2]/text()')[0]
                group_id = tr.xpath('./td[3]/a[1]/@href')[0]
                group_id = re.findall(r'edit/(.*?)$', group_id)[0]
                group['group_id'] = group_id
                group_list.append(group)
            except Exception as e:
                print(e)
                print('目前还没有分组信息')

        # print('现有分组信息如下：')
        # print(group_list)
        return group_list

    def add_group(self, group):
        post_url = 'https://www.tradewheel.com/member/ajax/products/group-add'
        get_url = 'https://www.tradewheel.com/member/products/groups/add'
        token = self.get(get_url)
        # print(token)
        response = self.session.post(url=post_url, headers=headers, data={'_token': token, 'product_group_name': group, 'page_add': 'page'})
        print(response.url)
        print('分组信息添加成功')

    def release(self, result):
        """还是需要用之前的seeion发起post请求，实现发布商品"""
        # 先判断是否登录成功
        if result:
            # print('登陆成功，开始发布商品')
            files = {}
            # 遍历图片相关信息的列表
            for file in self.files:
                # 构建图片上传的格式
                ex_name = re.findall(r'.*?\.(.*?)$', file[1])[0]
                files['product_images[%s]' % file[0]] = (file[1], open(file[2], 'rb'), 'image/%s'%ex_name)
            print(files)
            # 获取传进来的分组，判断其是否在现有的分组信息中
            group = self.goods_data['product_group_id'].strip()
            if len(group) < 5 and len(group) > 0:
                print('商品分组信息须大于5个字符,请修改后重试')
                sys.exit()
            elif len(group) >= 5:
                group_list = self.get_group()
                num = 0
                for g in group_list:
                    if group == g['name']:
                        self.goods_data['product_group_id'] = str(g['group_id'])
                        break
                    else:
                        num += 1
                if num == len(group_list):
                    print('商品分组信息不存在，自动添加中')
                    self.add_group(group)
                    new_group_list = self.get_group()
                    print(new_group_list)
                    time.sleep(5)
                    for g in new_group_list:
                        if group == g['name']:
                            self.goods_data['product_group_id'] = str(g['group_id'])
                            break
            # 查询商品类目id
            industry = self.goods_data['industry_id']
            sql = 'select id from ind_info where name="%s";' % industry
            mysql_db = Mysql()
            res_name = mysql_db.get_all(sql)
            if len(res_name) > 0:
                self.goods_data['industry_id'] = res_name[0][0]
                print('开始添加商品')
                new_token = self.get(self.add_get_url)
                print(new_token)
                # self.goods_data['prduct_group'] = 2978
                self.goods_data['_token'] = new_token
                print(self.goods_data)
                headers1 = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
                    # 'Content-Type': 'multipart/form-data;boundary=----WebKitFormBoundaryjc9CIoXGyJyFc112'

                }
                res = self.session.post(url=self.add_post_url, headers=headers1, data=self.goods_data, files=files)

                if res.url == 'https://www.tradewheel.com/member/products':
                    print('商品添加成功!')
                else:
                    print('商品添加失败！!!')
            else:
                print('商品类目信息industry_id不正确，请修改重试')
        else:
            print('登录失败')

    def run(self):
        token = self.get(self.login_get_url)
        result = self.post(token)
        # new_token = self.get(self.add_get_url)
        self.release(result)
        # self.get_group()






