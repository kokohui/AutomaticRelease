from TW_post import ReleaseGoods


id_email = '333333@qq.com'   # 这个邮箱是您要用来发布商品的账号邮箱
# 这个列表是需要上传的图片的相关信息,注意元素都是字符串格式，引号别忘了，建议将图片放到当前目录下的image中，写路径会方便一点
files = [
    # 格式：（第几张，图片名称，绝对路径）
    ('1', '123.jpeg', './image/123.jpeg'),
    ('2', 'car.png', './image/car.png'),
]

# 这个字典数据是您要发布的商品相关的信息
goods_data = {
    'industry_id': "Glass Cutter",  # 对应网页上的Select Industry，只需要填最后一级就行，比如：Security & Protection / Roadway Safety / Convex Mirror /,只需要填 Convex Mirror
    'name': '333',         # 对应的是Title,注意：标题不能是中文，貌似会无法进入详情页
    'product_group_id': '漂亮的袜子',    # 对应Product Group，5个字符以上，如果不要分组就空字符串
    'description': '<p> 鞋子 </p>',   # 对应details
    'keywords': '33',
    'min_price': '33',
    'max_price': '33',
    'price_unit': '33',
    'min_order': '33',
    'min_order_unit': '33',
    'port': '',
    'packaging': '',
    'lead_time': '',
    'attribute_label[]': '3',    # 这个对应的是对应网页上的Attributes的第一个输入框
    'attribute_value[]': '33',    # 这个对应的是对应网页上的Attributes的第二个输入框
    'showcase': '0',    # 0代表no， 1代表yes

}
release_goods = ReleaseGoods(id_email, goods_data, files)
release_goods.run()