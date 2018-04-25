from django.contrib import admin
from apps.goods.models import GoodsCategory, GoodsSKU, IndexSlideGoods, GoodsSPU, IndexCategoryGoods, IndexPromotion

admin.site.register(GoodsCategory)
admin.site.register(GoodsSPU)
admin.site.register(GoodsSKU)
admin.site.register(IndexSlideGoods)
admin.site.register(IndexCategoryGoods)
admin.site.register(IndexPromotion)

