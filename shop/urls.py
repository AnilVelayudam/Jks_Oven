from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('sweet-hub/', views.sweet_hub, name='sweet_hub'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/', views.order_success, name='order_success'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('review/<int:product_id>/', views.add_review, name='add_review'),
    path('category/<str:category>/', views.category_products, name='category_products'),
    path('search-products/', views.search_products, name='search_products'),
    path('increase/<int:product_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease/<int:product_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order-success/', views.order_success, name='order_success'),
    path("add-address/", views.add_address, name="add_address"),
    path("addresses/",views.addresses,name="addresses")
]

