from django.conf.urls import url, include
from apps.users import views

urlpatterns = [
    # 视图函数
    # url(r'^register$', views.register, name='register'),
    # url(r'^do_register$', views.do_register, name='do_register'),

    # 类视图函数:as_view() 返回一个视图函数  注意：不要加括号
    url(r'^register$', views.RegisterView.as_view(), name='register'),
    url(r'^active/(.+)$', views.ActiveView.as_view(), name='active'),
]

