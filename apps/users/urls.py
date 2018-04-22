from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required

from apps.users import views

urlpatterns = [
    # 视图函数
    # url(r'^register$', views.register, name='register'),
    # url(r'^do_register$', views.do_register, name='do_register'),

    # 类视图函数:as_view() 返回一个视图函数  注意：不要加括号
    url(r'^register$', views.RegisterView.as_view(), name='register'),
    url(r'^active/(.+)$', views.ActiveView.as_view(), name='active'),
    url(r'^send_message$', views.send_message, name='send_message'),
    url(r'^login$', views.LoginView.as_view(), name='login'),
    url(r'^login_out$', views.LoginoutView.as_view(), name='login_out'),
    url(r'^orders$', views.UserOrderView.as_view(), name='orders'),
    url(r'^address$', views.UserAddressView.as_view(), name='address'),
    # url(r'^address$', login_required(views.UserAddressView.as_view()), name='address'),
    url(r'^$', views.UserInfoView.as_view(), name='info'),
]

