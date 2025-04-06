from django.contrib import admin
from django.db.models import Count
from . import models


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["title", "unit_price", "inventory_status", "collection"]
    list_per_page = 10

    @admin.display(ordering="inventory")
    def inventory_status(self, obj):
        return obj.inventory > 10 and "Ok" or "Low"


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "membership"]
    list_editable = ["membership"]
    list_per_page = 10


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["title", "product_count"]
    list_per_page = 10

    @admin.display(ordering="products__count")
    def product_count(self, obj):
        return obj.products__count

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products__count=Count("product"))


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "placed_at", "customer"]
    list_select_related = ["customer"]
    list_per_page = 10
