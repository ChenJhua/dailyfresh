from django.conf.urls import url, include

from apps.goods import views

urlpatterns = [
    # url(r'^index$', views.index, name='index'),
    url(r'^index$', views.IndexView.as_view(), name='index'),
    url(r'^detail/(\d+)$', views.DetailView.as_view(), name='detail'),
]

