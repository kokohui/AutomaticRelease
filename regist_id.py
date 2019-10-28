from TW_post import Register


# 这个字典是用来装注册用的数据的, 这些数据一一对应注册页面那几个输入框，所有数据填入引号内
reg_data = {
    'name': '小ge',    # 名称
    'company_name': '',  # 这个貌似可以为空
    'phone_number': '18880888089',  # 电话号码
    'mobile_number': '',  # 这个貌似可以为空
    'key_products': '',  # 这个貌似可以为空
    'country_id': '43',     # 1-247中的任意数字可选，代表不同国家或地区
    'email': '3333332@qq.com',   # 注册邮箱
    'password': '123',      # 登录密码
    'messenger_type': 'qq',  # 这个可以为空，或者（skype，qq，wechat，whatsapp）4个中选一个
    'messenger_id': '111111',    # 这个貌似可以为空
}
register = Register(reg_data)
register.run()