from django.contrib import admin
from .models import Product, Order, OrderItem, Review, Address, ProductImage

# ---------------- PRODUCT ----------------
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

admin.site.register(Product, ProductAdmin)

# ---------------- ORDER ----------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_amount", "status", "payment_method", "payment_status")
    list_filter = ("status", "payment_method", "payment_status")

# ---------------- OTHERS ----------------
admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(Address)