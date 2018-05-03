from django.core.urlresolvers import reverse
from django.db import transaction
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from django_redis import get_redis_connection
from redis import StrictRedis

from apps.goods.models import GoodsSKU
from apps.orders.models import OrderInfo, OrderGoods
from apps.users.models import Address
from utils.common import LoginRequireMixin

from datetime import datetime


class PlaceOrderView(LoginRequireMixin, View):
    def post(self, request):
        # 获取请求参数：sku_ids
        count = request.POST.get('count')
        sku_ids = request.POST.getlist('sku_ids')

        # 校验参数不能为空
        if not sku_ids:
            return redirect(reverse('cart:info'))

        # 获取用户地址信息(此处使用最新添加的地址)
        try:
            address = Address.objects.filter(user=request.user).latest('create_time')
        except:
            # 查询不到地址信息，则用户需要点击页面中的按钮，新增地址
            address = None

        # todo: 查询购物车中的所有的商品
        skus = []  # 商品列表
        total_count = 0  # 商品总数量
        total_amount = 0  # 商品总金额

        strict_redis = get_redis_connection()  # type:StrictRedis
        key = 'cart_%s' % request.user.id
        # 从购物车页面过来
        if count is None:
            # 循环操作每一个订单商品
            for sku_id in sku_ids:
                # 查询一个商品对象
                try:
                    sku = GoodsSKU.objects.get(id=sku_id)
                except GoodsSKU.DoesNotExist:
                    return redirect(reverse('cart:info'))
                # 获取商品数量和小计金额(需要进行数据类型转换)
                count = strict_redis.hget(key, sku_id)  # bytes
                count = int(count)
                amount = sku.price * count

                # 新增实例属性,以便在模板界面中显示
                sku.count = count
                sku.amount = amount

                # 添加商品对象到列表中
                skus.append(sku)
                # 累计商品总数量和总金额
                total_count += sku.count
                total_amount += sku.amount

        else:
            # 详情页跳转过来
            sku_id = request.POST.get('sku_ids')
            # 查询一个商品对象
            try:
                sku = GoodsSKU.objects.get(id=sku_id)
            except GoodsSKU.DoesNotExist:
                return redirect(reverse('cart:info'))
            # 获取商品数量和小计金额(需要进行数据类型转换)
            count = int(count)
            amount = sku.price * count

            # 判断库存
            if count > sku.stock:
                # 库存不足，跳转回详情页面
                return redirect(reverse('goods:detail', args=[sku_id]))

            # 新增实例属性,以便在模板界面中显示
            sku.count = count
            sku.amount = amount

            # 添加商品对象到列表中
            skus.append(sku)
            # 累计商品总数量和总金额
            total_count += sku.count
            total_amount += sku.amount
            # 将商品数量保存到redis中
            strict_redis.hset(key, sku_id, count)

        # 运费(运费模块)
        trans_cost = 10
        # 实付金额
        total_pay = total_amount + trans_cost

        sku_ids_str = ','.join(sku_ids)

        # 定义模板显示的字典数据
        context = {
            'skus': skus,
            'address': address,
            'total_count': total_count,
            'total_amount': total_amount,
            'total_pay': total_pay,
            'trans_cost': trans_cost,
            'sku_ids_str': sku_ids_str,
        }
        # 响应结果: 返回确认订单html界面
        return render(request, 'place_order.html', context)


class CommitOrderView(View):
    """提交订单"""

    @transaction.atomic
    def post(self, request):
        # 登录判断
        if not request.user.is_authenticated():
            return JsonResponse({'code': 1, 'errmsg': '请先登录'})

        # 获取请求参数：address_id, pay_method, sku_ids_str
        address_id = request.POST.get('address_id')
        pay_method = request.POST.get('pay_method')
        sku_ids_str = request.POST.get('sku_ids_str')

        # 校验参数不能为空
        if not all([address_id, pay_method, sku_ids_str]):
            return JsonResponse({'code': 2, 'errmsg': '参数不能为空'})
        # 判断地址是否存在
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return JsonResponse({'code': 3, 'errmsg': '该地址不存在'})

        # 新增保存点
        point = transaction.savepoint()

        try:
            # todo: 修改订单信息表: 保存订单数据到订单信息表中(新增一条数据)
            total_count = 0
            total_amount = 0
            trans_cost = 10

            # 当前时间+用户id
            order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(request.user.id)
            order = OrderInfo.objects.create(
                order_id=order_id,
                total_count=total_count,
                total_amount=total_amount,
                trans_cost=trans_cost,
                pay_method=pay_method,
                user=request.user,
                address=address,
            )

            # 从Redis查询出购物车数据
            # 注意: 返回的是字典, 键值都为bytes类型
            # cart_1 = {1: 2, 2: 2}
            strict_redis = get_redis_connection()  # type:StrictRedis
            key = 'cart_%s' % request.user.id

            sku_ids = sku_ids_str.split(',')  # str->list
            # todo: 核心业务: 遍历每一个商品, 并保存到订单商品表
            for sku_id in sku_ids:
                # 查询订单中的每一个商品
                try:
                    sku = GoodsSKU.objects.get(id=sku_id)
                except GoodsSKU.DoesNotExist:
                    # 回滚到保存点，撤销所有的sql操作
                    transaction.savepoint_rollback(point)
                    return JsonResponse({'code': 4, 'errmsg': '商品不存在'})
                # 获取商品数量，并判断库存
                count = strict_redis.hget(key, sku_id)
                count = int(count)
                if count > sku.stock:
                    # 回滚到保存点，撤销所有的sql操作
                    transaction.savepoint_rollback(point)
                    return JsonResponse({'code': 5, 'errmsg': '库存不足'})

                # todo: 修改订单商品表: 保存订单商品到订单商品表（新增多条数据）
                OrderGoods.objects.create(
                    count=count,
                    price=sku.price,
                    order=order,
                    sku=sku,
                )

                # todo: 修改商品sku表: 减少商品库存, 增加商品销量
                sku.stock -= count
                sku.sales += count
                sku.save()

                # 累加商品数量和总金额
                total_count += count
                total_amount += (sku.price * count)

            # todo: 修改订单信息表: 修改商品总数量和总金额
            order.total_count = total_count
            order.total_amount = total_amount
            order.save()
        except:
            # 回滚到保存点，撤销所有的sql操作
            transaction.savepoint_rollback(point)
            return JsonResponse({'code': 6, 'errmsg': '创建订单失败'})
        transaction.savepoint_commit(point)
        # 从Redis中删除购物车中的商品
        # cart_1 = {1: 2, 2: 2}
        # redis命令: hdel cart_1 1 2
        # 列表 -> 位置参数
        strict_redis.hdel(key, *sku_ids)
        # 订单创建成功， 响应请求，返回json
        return JsonResponse({'code': 0, 'message': '创建订单成功'})












