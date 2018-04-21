# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_testmodel_goods_detail'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('receiver_name', models.CharField(max_length=20, verbose_name='收件人')),
                ('receiver_mobile', models.CharField(max_length=11, verbose_name='联系电话')),
                ('detail_addr', models.CharField(max_length=256, verbose_name='详细地址')),
                ('zip_code', models.CharField(max_length=6, null=True, verbose_name='邮政编码')),
                ('is_default', models.BooleanField(default=False, verbose_name='默认地址')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='所属用户')),
            ],
            options={
                'db_table': 'df_address',
            },
        ),
    ]
