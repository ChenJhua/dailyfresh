# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='testmodel',
            name='goods_detail',
            field=tinymce.models.HTMLField(verbose_name='商品详情', default=''),
        ),
    ]
