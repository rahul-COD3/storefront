from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.contenttypes.admin import GenericTabularInline
from store.admin import ProductAdmin
from store.models import Product
from tags.models import TaggedItem
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("first_name", "last_name", "email", "username", "usable_password", "password1", "password2"),
            },
        ),
    )

class TagInline(GenericTabularInline):
    autocomplete_fields = ["tag"]
    model = TaggedItem
    extra = 0

class CustomProductAdmin(ProductAdmin):
    inlines = [TagInline]
    
admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)


