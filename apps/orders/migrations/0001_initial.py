# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OrderGoods',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(verbose_name='修改时间', auto_now=True)),
                ('count', models.IntegerField(verbose_name='购买数量', default=1)),
                ('price', models.DecimalField(decimal_places=2, verbose_name='单价', max_digits=10)),
                ('comment', models.TextField(verbose_name='评价信息', default='')),
            ],
            options={
                'db_table': 'df_order_goods',
            },
        ),
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(verbose_name='修改时间', auto_now=True)),
                ('order_id', models.CharField(primary_key=True, serialize=False, verbose_name='订单号', max_length=64)),
                ('total_count', models.IntegerField(verbose_name='商品总数', default=1)),
                ('total_amount', models.DecimalField(decimal_places=2, verbose_name='商品总金额', max_digits=10)),
                ('trans_cost', models.DecimalField(decimal_places=2, verbose_name='运费', max_digits=10)),
                ('pay_method', models.SmallIntegerField(choices=[(1, '货到付款'), (2, '微信支付'), (3, '支付宝'), (4, '银联支付')], verbose_name='支付方式', default=1)),
                ('status', models.SmallIntegerField(choices=[(1, '待支付'), (2, '待发货'), (3, '待收货'), (4, '待评价'), (5, '已完成')], verbose_name='订单状态', default=1)),
                ('trade_no', models.CharField(verbose_name='支付编号', blank=True, null=True, unique=True, default='', max_length=100)),
            ],
            options={
                'db_table': 'df_order_info',
            },
        ),
    ]
