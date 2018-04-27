# # 添加到celery服务器所在电脑的项目中,
# # 让celery执行发送邮件前初始化django环境,没有部署再服务器里面，所以需要初始化
# import os
# import django
# # 设置环境变量
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
# # 初始化django环境
# django.setup()

from time import sleep
from celery import Celery
from django.core.mail import send_mail
from django.conf import settings

# 创建celery应用对象
from django.template import loader
from apps.goods.models import GoodsCategory, IndexSlideGoods, IndexPromotion, IndexCategoryGoods

app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/1')


@app.task
def send_active_email(username, email, token):
    """封装发送邮件方法"""

    subject = "天天生鲜用户激活"     # 标题,必须指定
    message = ""                  # 邮件正文(纯文本)
    sender = settings.EMAIL_FROM  # 发件人
    receivers = [email]           # 接收人, 需要是列表
    # 邮件正文(带html样式)
    html_message = '<h2>尊敬的 %s, 感谢注册天天生鲜</h2>' \
                   '<p>请点击此链接激活您的帐号: ' \
                   '<a href="http://127.0.0.1:8000/user/active/%s">' \
                   'http://127.0.0.1:8000/user/active/%s</a>' \
                   % (username, token, token)
    send_mail(subject, message, sender, receivers, html_message=html_message)


@app.task
def generate_static_index_page():
    """生成静态首页"""
    sleep(2)
    # 查询首页商品数据:商品类别/轮播图/促销活动
    categories = GoodsCategory.objects.all()
    slide_skus = IndexSlideGoods.objects.all().order_by('index')
    promotions = IndexPromotion.objects.all().order_by('index')[0:2]

    for category in categories:
        # 查询当前类型所有的文字商品和图片商品
        text_skus = IndexCategoryGoods.objects.filter(display_type=0, category=category)
        image_skus = IndexCategoryGoods.objects.filter(display_type=1, category=category)[0:4]

        # 动态给对象新增实例属性
        category.text_skus = text_skus
        category.image_skus = image_skus

    # 获取用户添加到购物车商品的总数量
    cart_count = 0

    # 定义模板显示的数据
    context = {
        'categories': categories,
        'slide_skus': slide_skus,
        'promotions': promotions,
        'cart_count': cart_count,
    }

    # 渲染生成静态的首页:index.html
    template = loader.get_template('index.html')
    html_str = template.render(context)
    # 生成首页
    path = '/home/python/Desktop/static/index.html'
    with open(path, 'w') as f:
        f.write(html_str)




