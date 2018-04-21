# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0003_address'),
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderGoods',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('count', models.IntegerField(default=1, verbose_name='购买数量')),
                ('price', models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')),
                ('comment', models.TextField(default='', verbose_name='评价信息')),
            ],
            options={
                'db_table': 'df_order_goods',
            },
        ),
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('order_id', models.CharField(max_length=64, primary_key=True, serialize=False, verbose_name='订单号')),
                ('total_count', models.IntegerField(default=1, verbose_name='商品总数')),
                ('total_amount', models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品总金额')),
                ('trans_cost', models.DecimalField(max_digits=10, decimal_places=2, verbose_name='运费')),
                ('pay_method', models.SmallIntegerField(default=1, choices=[(1, '货到付款'), (2, '微信支付'), (3, '支付宝'), (4, '银联支付')], verbose_name='支付方式')),
                ('status', models.SmallIntegerField(default=1, choices=[(1, '待支付'), (2, '待发货'), (3, '待收货'), (4, '待评价'), (5, '已完成')], verbose_name='订单状态')),
                ('trade_no', models.CharField(default='', verbose_name='支付编号', blank=True, unique=True, null=True, max_length=100)),
                ('address', models.ForeignKey(to='users.Address', verbose_name='收货地址')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='下单用户')),
            ],
            options={
                'db_table': 'df_order_info',
            },
        ),
        migrations.AddField(
            model_name='ordergoods',
            name='order',
            field=models.ForeignKey(to='orders.OrderInfo', verbose_name='所属订单'),
        ),
        migrations.AddField(
            model_name='ordergoods',
            name='sku',
            field=models.ForeignKey(to='goods.GoodsSKU', verbose_name='订单商品'),
        ),
    ]
