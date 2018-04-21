import re

from django.core.mail import send_mail
from django.core.signing import SignatureExpired
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View
from itsdangerous import TimedJSONWebSignatureSerializer

from apps.users.models import User
from celery_tasks.tasks import send_active_email
from dailyfresh import settings


def register(request):
    """
    进入注册页面
    :return: 注册页面的html
    """
    return render(request, 'register.html')


def do_register(request):
    """
    对注册页面发送过来的form表单数据进行处理
    :return:
    """
    # 获取post请求参数
    username = request.POST.get('username')
    password = request.POST.get('password')
    password2 = request.POST.get('password2')
    email = request.POST.get('email')
    allow = request.POST.get('allow')  # 用户协议，勾选后得到：on
    # todo:检验参数合法性
    # 判断参数不能为空
    if not all([username, password, password2, email]):
        return render(request, 'register.html', {'errmsg': "注册信息不能为空"})
    # 判断两次输入的密码是否一致
    if password != password2:
        return render(request, 'register.html', {'errmsg': "两次密码不一致"})
    # 判断邮箱合法
    if not re.match('^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        return render(request, 'register.html', {'errmsg': "邮箱不合法"})
    # 判断是否勾选用户协议
    if allow != 'on':
        return render(request, 'register.html', {'errmsg': "请勾选用户协议"})
    # 处理业务：保存用户到数据表中
    # django提供的方法，会对密码进行加密
    try:
        user = User.objects.create_user(username, email, password)
        # 修改用户状态为未激活
        user.is_active = False
        user.save()
    except IntegrityError:
        # 判断用户是否存在
        return render(request, 'register.html', {'errmsg': "用户名已存在"})

    # todo:发送激活邮件
    return HttpResponse("注册成功！")


class RegisterView(View):
    """注册视图"""

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        """
        对注册页面发送过来的form表单数据进行处理
        :return:
        """
        # 获取post请求参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        allow = request.POST.get('allow')  # 用户协议，勾选后得到：on
        # todo:检验参数合法性
        # 判断参数不能为空
        if not all([username, password, password2, email]):
            return render(request, 'register.html', {'errmsg': "注册信息不能为空"})
        # 判断两次输入的密码是否一致
        if password != password2:
            return render(request, 'register.html', {'errmsg': "两次密码不一致"})
        # 判断邮箱合法
        if not re.match('^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': "邮箱不合法"})
        # 判断是否勾选用户协议
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': "请勾选用户协议"})
        # 处理业务：保存用户到数据表中
        # django提供的方法，会对密码进行加密
        user = None
        try:
            user = User.objects.create_user(username, email, password)  # type: User
            # 修改用户状态为未激活
            user.is_active = False
            user.save()
        except IntegrityError:
            # 判断用户是否存在
            return render(request, 'register.html', {'errmsg': "用户名已存在"})

        # todo:发送激活邮件
        token = user.generate_active_token()
        # 同步发送：会阻塞
        # RegisterView.send_active_email(username, email, token)
        # 使用celery异步发送：不会阻塞
        # 会保存方法名
        send_active_email.delay(username, email, token)

        return HttpResponse("注册成功！")

    @staticmethod
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


class ActiveView(View):
    """用户激活"""
    def get(self, request, token: str):
        """
        用户激活
        :param token: 对字典{'confirm': 用户id}进行加密后得到的字符串
        :return:
        """
        try:
            # 解密token
            s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 3600 * 24)
            # 获取用户id  字符串要转为bytes
            dict_data = s.loads(token.encode())
        except SignatureExpired:
            # 判断是否失效
            return HttpResponse("激活链接已经失效")
        user_id = dict_data.get('confirm')
        # 修改字段为已激活
        User.objects.filter(id=user_id).update(is_active=True)
        # 响应请求
        return HttpResponse("激活成功，跳转到登录页")








