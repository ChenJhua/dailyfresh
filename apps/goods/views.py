from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.generic import View

from apps.users.models import User


class IndexView(View):
    def get(self, request):
        # 方式1：主动查询登录用户并显示
        # user_id = request.session.get('_auth_user_id')
        # user = User.objects.filter(id=user_id)
        # context = {'user': user}
        # return render(request, 'index.html', context)

        # 方式2：使用django用户验证模块，直接显示
        # django会自动查询登录的用户对象，会保存到request对象中
        # user = request.user

        return render(request, 'index.html')


