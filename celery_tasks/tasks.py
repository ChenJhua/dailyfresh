# # 添加到celery服务器所在电脑的项目中,
# # 让celery执行发送邮件前初始化django环境,没有部署再服务器里面，所以需要初始化
# import os
# import django
# # 设置环境变量
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
# # 初始化django环境
# django.setup()


from celery import Celery
from django.core.mail import send_mail
from django.conf import settings

# 创建celery应用对象
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




