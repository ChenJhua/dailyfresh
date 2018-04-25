import json
import random
import re

from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.core.signing import SignatureExpired
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from django_redis import get_redis_connection
from itsdangerous import TimedJSONWebSignatureSerializer

from apps.goods.models import GoodsSKU
from apps.users.models import User, Address
from celery_tasks.tasks import send_active_email
from dailyfresh import settings

import http.client
import urllib.request

from utils.common import LoginRequireView, LoginRequireMixin
from geetest import GeetestLib  # 极验验证


# 请在官网申请ID使用，示例ID不可使用
pc_geetest_id = "9107cbe379daa19cd93b9250f36ba301"  # id
pc_geetest_key = "73dd706e795ba4e67bad328cf6e68970"  # key


# 请求的路径
host = "106.ihuyi.com"
sms_send_uri = "/webservice/sms.php?method=Submit"
# 用户名是登录ihuyi.com账号名（例如：cf_demo123）
account = "C44569738"
# 密码 查看密码请登录用户中心->验证码、通知短信->帐户及签名设置->APIKEY
password = "dddf8c8b0c844c6691024c3cf4d17030 "


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
        uphone = request.POST.get('mobile')
        code = request.POST.get('code')
        email = request.POST.get('email')
        allow = request.POST.get('allow')  # 用户协议，勾选后得到：on
        print('手机 验证码', uphone, code, request.session.get('message_code'))
        # todo:检验参数合法性
        # 判断参数不能为空
        if not all([username, password, password2, email, uphone, code]):
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
        # 判断手机输入是否正确
        if not re.match('^1[345678]\d{9}$', uphone):
            return render(request, 'register.html', {'errmsg': "手机输入不合法"})
        # 判断验证码是否正确
        if code != request.session.get('message_code'):
            return render(request, 'register.html', {'errmsg': "验证码校验错误"})
        # 处理业务：保存用户到数据表中
        # django提供的方法，会对密码进行加密
        user = User()
        try:
            user = User.objects.create_user(username, email, password, uphone=uphone)  # type: User
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

        subject = "天天生鲜用户激活"  # 标题,必须指定
        message = ""  # 邮件正文(纯文本)
        sender = settings.EMAIL_FROM  # 发件人
        receivers = [email]  # 接收人, 需要是列表
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


def send_message(request):
    """发送信息的视图函数"""
    # 获取ajax的get方法发送过来的手机号码
    mobile = request.GET.get('mobile')
    # 通过手机去查找用户是否已经注册
    user = User.objects.filter(uphone=mobile)
    if len(user) == 1:
        return JsonResponse({'msg': "该手机已经注册"})
    # 定义一个字符串,存储生成的6位数验证码
    message_code = ''
    for i in range(6):
        i = random.randint(0, 9)
        message_code += str(i)
    # 拼接成发出的短信
    text = "您的验证码是：" + message_code + "。请不要把验证码泄露给其他人。"
    # 把请求参数编码
    params = urllib.parse.urlencode(
        {'account': account, 'password': password, 'content': text, 'mobile': mobile, 'format': 'json'})
    # 请求头
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    # 通过全局的host去连接服务器
    conn = http.client.HTTPConnection(host, port=80, timeout=30)
    # 向连接后的服务器发送post请求,路径sms_send_uri是全局变量,参数,请求头
    conn.request("POST", sms_send_uri, params, headers)
    # 得到服务器的响应
    response = conn.getresponse()
    # 获取响应的数据
    response_str = response.read()
    # 关闭连接
    conn.close()
    # 把验证码放进session中
    request.session['message_code'] = message_code
    print(eval(response_str.decode()))
    # 使用eval把字符串转为json数据返回
    return JsonResponse(eval(response_str.decode()))


class LoginView(View):
    def get(self, request):
        """进入登录界面"""
        return render(request, 'login.html')

    def post(self, request):
        """处理登录操作"""
        # 获取post请求参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        # 检验合法性
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': "用户名和密码不能为空"})
        # 业务处理：登录
        user = authenticate(username=username, password=password)
        if user is None:
            # 判断用户名和密码是否正确
            return render(request, 'login.html', {'errmsg': "用户名或密码不正确"})
        if not user.is_active:
            # 用户是否激活
            return render(request, 'login.html', {'errmsg': "用户未激活"})

        # 登录成功， 使用session或保存用户登录状态
        # request.session['_auth_user_id'] = user.id
        # 使用django的login方法保存用户登录状态
        login(request, user)

        if remember == 'on':
            # 保持登录状态两周
            request.session.set_expiry(None)
        else:
            # 关闭浏览器后，登录状态失效
            request.session.set_expiry(0)

        # 登录成功后,要跳转到next指向的页面
        next = request.GET.get('next')
        if next:
            # 不为空则跳转到next指向的页面
            return redirect(next)
        else:
            # 为空,则默认跳转到首页
            # 响应请求
            # return redirect('/index')
            return redirect(reverse('goods:index'))


class LoginoutView(View):
    def get(self, request):
        """注销"""
        # 调用django的logout方法，实现退出，会清除登录用户的id(session键值对数据)
        logout(request)
        # return redirect('/index')
        return redirect(reverse('goods:index'))


class UserInfoView(LoginRequireMixin, View):
    def get(self, requeset):
        # 未登录跳到登录页面
        # if not requeset.user.is_authenticated():
        #     return redirect(reverse('users:login'))

        # todo:从Redis中读取当前登录用户浏览过的商品
        # 返回一个StrictRedis
        # strict_redis = get_redis_connection('default')
        strict_redis = get_redis_connection()  # type:StrictRedis
        # 读取所有的商品id,返回一个列表
        # history_id = [商品id1,商品id2,商品id3]
        key = 'history_%s' % requeset.user.id
        # 最多只取出5个商品id
        sku_ids = strict_redis.lrange(key, 0, 4)
        print(sku_ids)
        # 顺序问题:根据商品id,查询出商品对象
        # 这行会影响添加进去的顺序
        # skus = GoodsSKU.objects.filter(id__in=sku_ids)
        # 解决:
        skus = []  # 用来保存查询出来的商品对象
        for sku_id in sku_ids:  # sku_id　byte
            sku = GoodsSKU.objects.get(id=sku_id)
            skus.append(sku)

        # 查询最新的地址显示
        try:
            # 查询登录用户最新添加的地址,并显示出来
            # address = Address.objects.filter(user=requeset.user).order_by('create_time]')[0]
            address = requeset.user.address_set.latest('create_time')
        except Exception:
            address = None
        context = {
            'address': address,
            'which_page': '1',
            'skus': skus,
        }
        return render(requeset, 'user_center_info.html', context)


class UserOrderView(LoginRequireMixin, View):
    def get(self, requeset):
        context = {'which_page': '2'}
        return render(requeset, 'user_center_order.html', context)


class UserAddressView(LoginRequireMixin, View):
    def get(self, requeset):
        # 查询登录用户最新添加的地址,并显示出来
        user = requeset.user
        try:
            # 查询登录用户最新添加的地址,并显示出来
            # address = Address.objects.filter(user=requeset.user).order_by('create_time]')[0]
            address = user.address_set.latest('create_time')
        except Exception:
            address = None

        context = {
            'address': address,
            'which_page': '3',
        }
        return render(requeset, 'user_center_site.html', context)

    def post(self, request):
        # 获取参数
        receiver = request.POST.get('receiver')
        detail = request.POST.get('detail')
        zip_code = request.POST.get('zip_code')
        mobile = request.POST.get('mobile')

        # 判断是否为空
        if not all([receiver, detail, zip_code, mobile]):
            return render(request, 'user_center_site.html', {'errmsg': "参数不能为空"})

        # 新增一个地址
        Address.objects.create(
            receiver_name=receiver,
            detail_addr=detail,
            receiver_mobile=mobile,
            zip_code=zip_code,
            user=request.user,
        )

        # 添加成功后,回到当前页面,刷新数据
        return redirect(reverse('users:address'))


def pcgetcaptcha(request):
    """极验验证函数"""
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)






