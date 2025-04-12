from django.contrib import admin, messages
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html, urlencode
from . import models


class InventoryFilter(admin.SimpleListFilter):
    title = "inventory"
    parameter_name = "inventory"

    def lookups(self, request, model_admin):
        return [("<10", "Low"), (">10", "Ok")]

    def queryset(self, request, queryset):
        if self.value() == "<10":
            return queryset.filter(inventory__lt=10)
        if self.value() == ">10":
            return queryset.filter(inventory__gt=10)

class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ["product"]
    min_num = 1
    extra = 0
    model = models.OrderItem

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ["collection"]
    prepopulated_fields = {
        "slug": ["title"],
    }
    actions = ["clear_inventory"]
    list_display = [
        "title",
        "inventory",
        "unit_price",
        "inventory_status",
        "collection"
    ]
    list_per_page = 10
    list_filter = ["collection", "last_update", InventoryFilter]
    search_fields = ["title"]

    @admin.display(ordering="inventory")
    def inventory_status(self, obj):
        return obj.inventory > 10 and "Ok" or "Low"

    @admin.action(description="Clear inventory")
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)

        self.message_user(
            request,
            f"{updated_count} products were successfully updated.",
            messages.SUCCESS,
        )

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["user__first_name", "membership", "orders"]
    list_editable = ["membership"]
    list_per_page = 10
    ordering = ["user__first_name", "user__last_name"]
    search_fields = ["user__first_name__istartswith"]

    def orders(self, obj):
        url = f"{reverse('admin:store_order_changelist')}?{urlencode({'customer__id': obj.id})}"
        return format_html("<a href='{}'>{}</a>", url, obj.orders)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(orders=Count("order"))


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["title", "product_count"]
    list_per_page = 10
    search_fields = ["title"]

    @admin.display(ordering="products__count")
    def product_count(self, obj):
        url = f"{reverse('admin:store_product_changelist')}?{urlencode({'collection__id': obj.id})}"
        return format_html("<a href='{}'>{}</a>", url, obj.products_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count("products"))


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ["customer"]
    inlines = [OrderItemInline]
    list_display = ["id", "placed_at", "customer"]
    list_select_related = ["customer"]
    list_per_page = 10
