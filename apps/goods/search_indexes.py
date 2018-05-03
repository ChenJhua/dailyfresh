from haystack import indexes
from .models import GoodsSKU


class GoodsSKUIndex(indexes.SearchIndex, indexes.Indexable):
    """模型索引类： 针对哪张表的哪些数据创建索引"""

    # 参数2： 通过模板来指定要对哪些表字段数据创建索引
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        """商品SKU模型类，对应商品SKU表"""
        return GoodsSKU

    def index_queryset(self, using=None):
        """要对表中的哪些数据创建索引"""
        # return self.get_model().objects.all()
        # 针对上线的商品(未下架的商品)创建索引
        return self.get_model().objects.filter(status=True)




