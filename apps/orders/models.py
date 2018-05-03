from django.db import models
from apps.goods.models import GoodsSKU
from apps.users.models import User, Address
from utils.models import BaseModel


class OrderInfo(BaseModel):
    """订单信息"""

    PAY_METHODS = {
        '1': "货到付款",
        '2': "微信支付",
        '3': "支付宝",
        '4': "银联支付",
    }

    PAY_METHOD_CHOICES = (
        (1, "货到付款"),
        (2, "微信支付"),
        (3, "支付宝"),
        (4, "银联支付"),
    )

    ORDER_STATUS = {
        1: "待支付",
        2: "待发货",
        3: "待收货",
        4: "待评价",
        5: "已完成",
    }

    ORDER_STATUS_CHOICES = (
        (1, "待支付"),
        (2, "待发货"),
        (3, "待收货"),
        (4, "待评价"),
        (5, "已完成"),
    )
    # 指定了primary_key后，不会自动生成主键
    order_id = models.CharField(max_length=64,
                                primary_key=True,
                                verbose_name="订单号")
    total_count = models.IntegerField(default=1, verbose_name="商品总数")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2,
                                       verbose_name="商品总金额")
    trans_cost = models.DecimalField(max_digits=10, decimal_places=2,
                                     verbose_name="运费")
    pay_method = models.SmallIntegerField(choices=PAY_METHOD_CHOICES,
                                          default=1, verbose_name="支付方式")
    status = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES,
                                      default=1, verbose_name="订单状态")
    trade_no = models.CharField(max_length=100, default='',
                                null=True,
                                blank=True, verbose_name="支付编号")
    user = models.ForeignKey(User, verbose_name="下单用户")
    address = models.ForeignKey(Address, verbose_name="收货地址")

    class Meta:
        db_table = "df_order_info"


class OrderGoods(BaseModel):
    """订单商品"""
    count = models.IntegerField(default=1, verbose_name="购买数量")
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                verbose_name="单价")
    comment = models.TextField(default="", verbose_name="评价信息")
    order = models.ForeignKey(OrderInfo, verbose_name="所属订单")
    sku = models.ForeignKey(GoodsSKU, verbose_name="订单商品")

    class Meta:
        db_table = "df_order_goods"
