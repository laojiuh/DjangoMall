from django.contrib import admin
# Register your models here.
from mall.forms import ProductAdminForm
from mall.models import Product, Classify, Tag

from utils.admin_actions import set_invalid, set_valid


# 方式1：用装饰器
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """ 商品信息管理 """
    list_display = ('name', 'types', 'price', 'status', 'is_valid')
    # 修改分页的大小
    list_per_page = 5
    # 添加过滤器搜索
    list_filter = ('status',)
    # 排除某些字段，使其不可编辑
    # exclude = ['remain_count']
    # 不可编辑，但是可以看见到数据
    readonly_fields = ['remain_count']
    actions = [set_invalid, set_valid]
    # 自定义表单
    form = ProductAdminForm


# 方式2：注册后台管理
# admin.site.register(Product, ProductAdmin)

@admin.register(Classify)
class ClassifyAdmin(admin.ModelAdmin):
    """ 商品分类管理 """
    list_display = ('name', 'parent', 'code', 'is_valid')
    readonly_fields = ['uid']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """ 商品标签管理 """
    readonly_fields = ['uid']
    list_display = ('name', 'code', 'is_valid')