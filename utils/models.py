from django.db import models


class BaseModel(models.Model):
    """模型类父类"""

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="修改时间")

    class Meta(object):
        # 需要指定基类模型类为抽象的,否则迁移生成表时会出错
        abstract = True




