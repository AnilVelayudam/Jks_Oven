from django.shortcuts import render
from .models import Product

def home(request):

    featured_cakes = Product.objects.filter(category='cake')[:7]

    famous_items = Product.objects.all()

    return render(request, 'home.html', {
        'featured_cakes': featured_cakes,
        'famous_items': famous_items
    })
# def sweet_hub(request):
#     products = Product.objects.all()
#     return render(request, 'sweet_hub.html', {'products': products})

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, id=product_id)

    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1

    request.session['cart'] = cart

    return redirect(request.META.get('HTTP_REFERER'))

def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        total += product.price * quantity

        cart_items.append({
            'product': product,
            'quantity': quantity
        })

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })
from django.contrib.auth.decorators import login_required
from .models import Order

from .models import Order, OrderItem

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    total = 0

    # Calculate total
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        total += product.price * quantity

    if request.method == "POST":

        # Create Order
        order = Order.objects.create(
            user=request.user,
            total_amount=total
        )

        # 🔥 Create OrderItems
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

        # Clear cart
        request.session['cart'] = {}

        return redirect('order_success')

    return render(request, 'checkout.html', {'total': total})

def order_success(request):
    return render(request, 'order_success.html')

from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'profile.html', {'orders': orders})

from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import render, redirect

def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)
        return redirect('home')

    return render(request, 'register.html')

from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Review
from .forms import ReviewForm

# review 
def add_review(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":

        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()

    return redirect('product_detail', product_id=product.id)

from django.shortcuts import render, get_object_or_404
from .models import Product, Review

def product_detail(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    reviews = Review.objects.filter(product=product)

    return render(request, "product_detail.html", {
        "product": product,
        "reviews": reviews
    })

def sweet_hub(request):
    category = request.GET.get('category')
    
    if category:
        products = Product.objects.filter(category=category)
    else:
        products = Product.objects.all()

    return render(request, 'sweet_hub.html', {'products': products})

def category_products(request, category):

    products = Product.objects.filter(category=category)

    return render(request, "category_products.html", {
        "products": products,
        "category": category
    })