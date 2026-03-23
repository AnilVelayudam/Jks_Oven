from django.contrib import admin
from .models import Product, Order, OrderItem, Review
from .models import Address

# admin.site.register(Category)

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(Address)


from .models import Product, ProductImage
from django.contrib import admin

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3   # shows 3 upload boxes

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

admin.site.register(Product, ProductAdmin)