from django.contrib import admin
from .models import Product, Order, OrderItem, Review
from .models import Address

# admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(Address)