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
    path('increase/<str:key>/', views.increase_quantity, name='increase_quantity'),
    path('decrease/<str:key>/', views.decrease_quantity, name='decrease_quantity'),
    path('remove/<str:key>/', views.remove_from_cart, name='remove_from_cart'),
    path('order-success/', views.order_success, name='order_success'),
    path("add-address/", views.add_address, name="add_address"),
    path("addresses/",views.addresses,name="addresses"),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('buy-now-item/<str:key>/', views.buy_now_from_cart, name='buy_now_from_cart'),
    path('edit-address/<int:id>/', views.edit_address, name='edit_address'),
    path('delete-address/<int:id>/', views.delete_address, name='delete_address'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),
    path("razorpay-webhook/", views.razorpay_webhook, name="razorpay_webhook"),
    path("login/", views.login_view, name="login"),

   
]

