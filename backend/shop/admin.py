from django.contrib import admin
from .models import (
    Product,
    ProductOption,
    Order,
    OrderItem,
    Review,
    Address,
    ProductImage,
    DeliveryPincode,
)

# ---------------- PRODUCT IMAGE INLINE ----------------

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

class ProductOptionInline(admin.TabularInline):
    model = ProductOption
    extra = 1
    fields = ("option_name", "price")


# ---------------- PRODUCT ----------------

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    inlines = [ProductImageInline,
               ProductOptionInline,]

    class Media:
        js = ("js/product_admin.js",)

    list_display = (
        "name",
        "category",
        "price",
        "cookie_quantity",
        "cookie_pack_price",
        "whipping_price",
        "buttercream_price",
    )

    def get_fields(self, request, obj=None):

        fields = [
            "name",
            "category",
            "description",
            "image",
            "is_offer",
        ]

        # Existing product
        if obj:

            if obj.category == "cake":
                fields += [
                    "whipping_price",
                    "buttercream_price",
                ]

            elif obj.category == "cookie":
                fields += [
                    "cookie_quantity",
                    "cookie_pack_price",
                ]

            else:
                fields += [
                    "price",
                ]

        # New product
        else:

            fields += [
                "price",
                "cookie_quantity",
                "cookie_pack_price",
                "whipping_price",
                "buttercream_price",
            ]

        return fields


# ---------------- ORDER ----------------

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "total_amount",
        "status",
        "payment_method",
        "payment_status",
    )

    list_filter = (
        "status",
        "payment_method",
        "payment_status",
    )


# ---------------- OTHERS ----------------

admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(Address)
admin.site.register(DeliveryPincode)