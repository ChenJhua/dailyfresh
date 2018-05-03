from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from django_redis import get_redis_connection
from redis import StrictRedis

from apps.goods.models import GoodsCategory, IndexSlideGoods, IndexPromotion, IndexCategoryGoods, GoodsSKU
from apps.orders.models import OrderGoods
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
        # 读取Redis中的缓存数据
        context = cache.get('index_page_data')
        if not context:
            print('没有缓存,从mysql数据库中读取')
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

            # 定义要缓存的数据:字典
            context = {
                'categories': categories,
                'slide_skus': slide_skus,
                'promotions': promotions,
            }
            # 缓存数据:保存数据到Redis中
            # 参数1:键名
            # 参数2:要缓存的数据(字典)
            # 参数3:缓存时间:半个小时
            cache.set('index_page_data', context, 60*30)
        else:
            print('使用缓存')

        # 获取用户添加到购物车商品的总数量
        cart_count = self.get_cart_count(request)
        # 给字典新增一个键值
        # context.update({'cart_count': cart_count})
        context['cart_count'] = cart_count

        return render(request, 'index.html', context)


class DetailView(BaseCartView):
    def get(self, request, sku_id):
        """
        显示商品详情界面
        :param request:
        :param sku_id: 商品id
        :return:
        """
        # todo:查询数据库数据
        # 查询商品SKU信息
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            # 没有查询到商品跳转到首页
            return redirect(reverse('goods:index'))
        # 查询所有商品分类信息
        categories = GoodsCategory.objects.all()
        # 查询最新商品推荐  只查询两条
        try:
            new_skus = GoodsSKU.objects.filter(category=sku.category).order_by('-create_time')[0:2]
        except:
            new_skus = None
        # 如果已登录，查询购物车信息
        cart_count = self.get_cart_count(request)
        # todo:查询其他规格商品
        other_skus = GoodsSKU.objects.filter(spu=sku.spu).exclude(id=sku_id)

        # todo:保存用户浏览的商品到redis中
        if request.user.is_authenticated():
            # 获取StrictRedis对象
            strict_redis = get_redis_connection()  # type:StrictRedis
            # history_1 = [3, 1, 2]
            key = 'history_%s' % request.user.id
            # 删除list中已存在的商品id
            strict_redis.lrem(key, 0, sku_id)
            # 添加商品id到list的左侧
            strict_redis.lpush(key, sku_id)
            # 控制元素的个数:最多只保存5个商品记录
            strict_redis.ltrim(key, 0, 4)

        # 获取商品的评论信息
        order_skus = OrderGoods.objects.filter(sku=sku).exclude(comment='')

        context = {
            'sku': sku,
            'categories': categories,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'other_skus': other_skus,
            'order_skus': order_skus,
        }

        return render(request, 'detail.html', context)


class ListView(BaseCartView):
    """商品列表详情页"""
    def get(self, request, category_id, page_num):
        """
        显示商品列表页面
        :param request:
        :param category_id: 类别id
        :param page_num: 页码
        :return:
        """
        # 获取请求参数
        sort = request.GET.get('sort')
        # 校验参数合法性
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return redirect(reverse('goods:index'))

        # 业务:查询对应的商品数据

        # 商品分类信息
        categories = GoodsCategory.objects.all()

        # 新品推荐信息（在GoodsSKU表中，查询特定类别信息，按照时间倒序）
        try:
            new_skus = GoodsSKU.objects.filter(category=category).order_by('-create_time')[0:2]
        except:
            new_skus = None
        # 该类别下商品列表信息
        if sort == 'price':
            # 价格升序排
            skus = GoodsSKU.objects.filter(category=category).order_by('price')
        elif sort == 'hot':
            # 销量降序排
            skus = GoodsSKU.objects.filter(category=category).order_by('-sales')
        else:
            # 默认id升序排
            skus = GoodsSKU.objects.filter(category=category)
            sort = 'default'

        # todo:商品分页信息
        # 参数１：要分页的数据
        # 参数２：每页显示多少条
        paginator = Paginator(skus, 2)
        try:
            page = paginator.page(page_num)
        except EmptyPage:  # 页码出错
            # 出错默认显示第一页
            page = paginator.page(1)

        # 购物车信息
        cart_count = self.get_cart_count(request)
        # 响应请求
        context = {
            "category": category,
            "categories": categories,
            "new_skus": new_skus,
            # "skus": skus,
            "sort": sort,
            "cart_count": cart_count,
            "page": page,
            "page_range": paginator.page_range,

        }
        return render(request, 'list.html', context)


