from django.conf.urls import url, include

from apps.orders import views

urlpatterns = [
    url(r'^place$', views.PlaceOrderView.as_view(), name='place'),
    url(r'^commit$', views.CommitOrderView.as_view(), name='commit'),
    url(r'^pay$', views.OrderPayView.as_view(), name='pay'),
    url(r'^check$', views.OrderCheckView.as_view(), name='check'),
    # 商品评论
    url(r'^comment/(\d+)$', views.OrderCommentView.as_view(), name='comment'),
]

