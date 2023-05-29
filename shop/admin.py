from django.contrib import admin
from .models import Tag, Product, ProductOption


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "tag_set_list",
        "option_list",
    )


@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "product",
        "name",
        "price",
    )
