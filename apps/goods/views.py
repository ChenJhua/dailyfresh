from django.http.response import HttpResponse
from django.shortcuts import render


def index(request):
    """进入首页"""
    return HttpResponse('首页')


