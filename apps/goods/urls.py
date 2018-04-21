from django.conf.urls import url, include

from apps.goods import views

urlpatterns = [
    url(r'^index$', views.index, name='index'),
]

