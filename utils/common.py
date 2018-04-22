from django.contrib.auth.decorators import login_required
from django.views.generic import View


class LoginRequireView(View):
    """会做登录检测的类视图"""
    # 需要定义为一个类方法
    @classmethod
    def as_view(cls, **initkwargs):
        # 视图函数
        view_fun = super().as_view(**initkwargs)
        # 使用装饰器对视图函数进行装饰
        return login_required(view_fun)


# 混合:扩展/新增一个功能
class LoginRequireMixin(object):
    """会做登录检测的类视图"""
    # 需要定义为一个类方法
    @classmethod
    def as_view(cls, **initkwargs):
        # 视图函数 (object中并没有as_view方法,会调用View的as_view方法)
        view_fun = super().as_view(**initkwargs)
        # 使用装饰器对视图函数进行装饰
        return login_required(view_fun)









