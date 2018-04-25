from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.generic import View
from django_redis import get_redis_connection
from redis import StrictRedis

from apps.goods.models import GoodsCategory, IndexSlideGoods, IndexPromotion, IndexCategoryGoods
from apps.users.models import User


class BaseCartView(View):
    def get_cart_count(self, request):
        """获取用户购物车中商品的总数量"""
        # todo:读取用户添加到购物车中的商品总数量
        cart_count = 0  # 购物车商品总数量
        if request.user.is_authenticated():
            # 已登录
            strict_redis = get_redis_connection()  # type:StrictRedis
            # cart_1 = {1:2, 2:2}
            key = 'cart_%s' %request.user.id
            # 返回list类型,存储的是bytes类型数据 [2,2]
            vals = strict_redis.hvals(key)
            for count in vals:
                # count 为bytes
                cart_count += int(count)
        return cart_count


class IndexView(BaseCartView):
    def get2(self, request):
        # 方式1：主动查询登录用户并显示
        # user_id = request.session.get('_auth_user_id')
        # user = User.objects.filter(id=user_id)
        # context = {'user': user}
        # return render(request, 'index.html', context)

        # 方式2：使用django用户验证模块，直接显示
        # django会自动查询登录的用户对象，会保存到request对象中
        # user = request.user

        return render(request, 'index.html')

    def get(self, request):
        # 查询首页商品数据:商品类别/轮播图/促销活动
        categories = GoodsCategory.objects.all()
        slide_skus = IndexSlideGoods.objects.all().order_by('index')
        promotions = IndexPromotion.objects.all().order_by('index')[0:2]

        for category in categories:
            # 查询当前类型所有的文字商品和图片商品
            text_skus = IndexCategoryGoods.objects.filter(display_type=0, category=category)
            image_skus = IndexCategoryGoods.objects.filter(display_type=1, category=category)[0:4]

            # 动态给对象新增实例属性
            category.text_skus = text_skus
            category.image_skus = image_skus

        # 获取用户添加到购物车商品的总数量
        cart_count = self.get_cart_count(request)

        # 定义模板显示的数据
        context = {
            'categories': categories,
            'slide_skus': slide_skus,
            'promotions': promotions,
            'cart_count': cart_count,
        }
        return render(request, 'index.html', context)


