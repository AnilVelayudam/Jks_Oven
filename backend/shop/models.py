from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('cake', 'Cake'),
        ('cookie', 'Cookie'),
        ('icecream', 'Ice Cream'),
        ('sweet', 'Sweet'),
    ]

    CAKE_TYPE_CHOICES = [
    ('basic', 'Basic Cake'),
    ('premium', 'Premium Cake'),
    ('milk', 'Milk Cake / Tres Leches'),
    ]

    cake_type = models.CharField(
    max_length=20,
    choices=CAKE_TYPE_CHOICES,
    blank=True,
    null=True
    )

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    whipping_price = models.DecimalField(max_digits=10, decimal_places=2)
    buttercream_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    description = models.TextField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_offer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def average_rating(self):
        return self.review_set.aggregate(avg=Avg('rating'))['avg'] or 0

    def review_count(self):
        return self.review_set.count()
    
    def __str__(self):
        return self.name

class Address(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    pincode = models.CharField(max_length=10)

    house = models.CharField(max_length=200)
    area = models.CharField(max_length=200)
    landmark = models.CharField(max_length=200, blank=True)

    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)

    def __str__(self):
        return self.full_name
    
class Order(models.Model):

    # 🔥 DELIVERY STATUS
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PACKED", "Packed"),
        ("OUT_FOR_DELIVERY", "Out for Delivery"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    ]

    # 🔥 PAYMENT STATUS
    PAYMENT_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
        ("REFUNDED", "Refunded"),
    ]

    PAYMENT_CHOICES = [
        ("COD", "Cash on Delivery"),
        ("ONLINE", "Online Payment"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True)

    # ✅ DELIVERY STATUS
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="PENDING")

    # ✅ PAYMENT INFO
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default="COD")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="PENDING")
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    estimated_delivery = models.DateField(null=True, blank=True)


    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

from django.db import models
from django.contrib.auth.models import User

class Review(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    rating = models.IntegerField()
    comment = models.TextField()

    # 🔥 ADD THIS LINE (important)
    image = models.ImageField(upload_to='reviews/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return f"{self.product.name} Image"
    
