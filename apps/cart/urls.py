from django.conf.urls import url, include
from apps.cart import views

urlpatterns = [
    # 添加商品到购物车
    url(r'^add$', views.AddCartView.as_view(), name='add'),
    # 进入购物车页面
    url(r'^$', views.CartInfoView.as_view(), name='info'),
    # 更新购物车数据
    url(r'^update$', views.UpdateCartView.as_view(), name='update'),
    # 删除购物车数据
    url(r'^delete$', views.DeleteCartView.as_view(), name='delete'),
]

