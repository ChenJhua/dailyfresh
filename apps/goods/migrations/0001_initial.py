# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GoodsCategory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('name', models.CharField(max_length=20, verbose_name='类别名称')),
                ('logo', models.CharField(max_length=100, verbose_name='图标标识')),
                ('image', models.ImageField(upload_to='category', verbose_name='类别图片')),
            ],
            options={
                'db_table': 'df_goods_category',
                'verbose_name_plural': '商品类别',
                'verbose_name': '商品类别',
            },
        ),
        migrations.CreateModel(
            name='GoodsImage',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('image', models.ImageField(upload_to='goods', verbose_name='图片')),
            ],
            options={
                'db_table': 'df_goods_image',
                'verbose_name_plural': '商品图片',
                'verbose_name': '商品图片',
            },
        ),
        migrations.CreateModel(
            name='GoodsSKU',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('name', models.CharField(max_length=100, verbose_name='名称')),
                ('title', models.CharField(max_length=200, verbose_name='简介')),
                ('unit', models.CharField(max_length=10, verbose_name='销售单位')),
                ('price', models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')),
                ('stock', models.IntegerField(default=0, verbose_name='库存')),
                ('sales', models.IntegerField(default=0, verbose_name='销量')),
                ('default_image', models.ImageField(upload_to='goods', verbose_name='图片')),
                ('status', models.BooleanField(default=True, verbose_name='是否上线')),
                ('category', models.ForeignKey(to='goods.GoodsCategory', verbose_name='类别')),
            ],
            options={
                'db_table': 'df_goods_sku',
                'verbose_name_plural': '商品SKU',
                'verbose_name': '商品SKU',
            },
        ),
        migrations.CreateModel(
            name='GoodsSPU',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('name', models.CharField(max_length=100, verbose_name='名称')),
                ('desc', models.TextField(blank=True, default='', verbose_name='商品描述')),
            ],
            options={
                'db_table': 'df_goods_spu',
                'verbose_name_plural': '商品',
                'verbose_name': '商品',
            },
        ),
        migrations.CreateModel(
            name='IndexCategoryGoods',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('display_type', models.SmallIntegerField(choices=[(0, '标题'), (1, '图片')], verbose_name='展示类型')),
                ('index', models.SmallIntegerField(default=0, verbose_name='顺序')),
                ('category', models.ForeignKey(to='goods.GoodsCategory', verbose_name='商品类别')),
                ('sku', models.ForeignKey(to='goods.GoodsSKU', verbose_name='商品SKU')),
            ],
            options={
                'db_table': 'df_index_category_goods',
                'verbose_name_plural': '主页分类展示商品',
                'verbose_name': '主页分类展示商品',
            },
        ),
        migrations.CreateModel(
            name='IndexPromotion',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('name', models.CharField(max_length=50, verbose_name='活动名称')),
                ('url', models.CharField(max_length=100, verbose_name='活动连接')),
                ('image', models.ImageField(upload_to='banner', verbose_name='图片')),
                ('index', models.SmallIntegerField(default=0, verbose_name='顺序')),
            ],
            options={
                'db_table': 'df_index_promotion',
                'verbose_name_plural': '主页促销活动',
                'verbose_name': '主页促销活动',
            },
        ),
        migrations.CreateModel(
            name='IndexSlideGoods',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('image', models.ImageField(upload_to='banner', verbose_name='图片')),
                ('index', models.SmallIntegerField(default=0, verbose_name='顺序')),
                ('sku', models.ForeignKey(to='goods.GoodsSKU', verbose_name='商品SKU')),
            ],
            options={
                'db_table': 'df_index_slide_goods',
                'verbose_name_plural': '主页轮播商品',
                'verbose_name': '主页轮播商品',
            },
        ),
        migrations.AddField(
            model_name='goodssku',
            name='spu',
            field=models.ForeignKey(to='goods.GoodsSPU', verbose_name='商品SPU'),
        ),
        migrations.AddField(
            model_name='goodsimage',
            name='sku',
            field=models.ForeignKey(to='goods.GoodsSKU', verbose_name='商品SKU'),
        ),
    ]
