from django.shortcuts import render
from .models import Product

def home(request):

    featured_cakes = Product.objects.filter(category='cake')[:8]

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
            'quantity': quantity,
            'subtotal': product.price * quantity
        })

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })
from django.contrib.auth.decorators import login_required
from .models import Order

from .models import Order, OrderItem

from .models import Address

@login_required
def checkout(request):

    cart = request.session.get('cart', {})
    total = 0

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        total += product.price * quantity

    addresses = Address.objects.filter(user=request.user)

    if request.method == "POST":

        # save new address
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        address_line = request.POST.get("address_line")
        city = request.POST.get("city")
        state = request.POST.get("state")
        pincode = request.POST.get("pincode")

        if full_name:
            Address.objects.create(
                user=request.user,
                full_name=full_name,
                phone=phone,
                address_line=address_line,
                city=city,
                state=state,
                pincode=pincode
            )

        order = Order.objects.create(
            user=request.user,
            total_amount=total
        )
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

        request.session['cart'] = {}

        return redirect("order_success")

    return render(request, "checkout.html", {
        "total": total,
        "addresses": addresses
    })

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

    query = request.GET.get('q')

    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    return render(request, 'sweet_hub.html', {
        'products': products
    })
def category_products(request, category):

    products = Product.objects.filter(category=category)

    return render(request, "category_products.html", {
        "products": products,
        "category": category
    })


#Search functionality

from django.http import JsonResponse
from .models import Product

def search_products(request):

    query = request.GET.get('q')

    results = []

    if query:
        products = Product.objects.filter(name__icontains=query)[:5]

        for product in products:
            results.append({
                "id": product.id,
                "name": product.name,
                "price": str(product.price),
                "image": product.image.url if product.image else ""
            })

    return JsonResponse(results, safe=False)


def increase_quantity(request, product_id):

    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)] += 1

    request.session['cart'] = cart

    return redirect('cart')


def decrease_quantity(request, product_id):

    cart = request.session.get('cart', {})

    if str(product_id) in cart:

        cart[str(product_id)] -= 1

        if cart[str(product_id)] <= 0:
            del cart[str(product_id)]

    request.session['cart'] = cart

    return redirect('cart')


def remove_from_cart(request, product_id):

    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        del cart[str(product_id)]

    request.session['cart'] = cart

    return redirect('cart')


def order_success(request):
    return render(request, 'order_success.html')


from django.shortcuts import render, redirect
from .models import Address

def add_address(request):

    if request.method == "POST":

        Address.objects.create(
            user=request.user,
            full_name=request.POST.get("full_name"),
            phone=request.POST.get("phone"),
            pincode=request.POST.get("pincode"),
            house=request.POST.get("house"),
            area=request.POST.get("area"),
            landmark=request.POST.get("landmark"),
            city=request.POST.get("city"),
            state=request.POST.get("state"),
        )

        return redirect("checkout")

    return render(request, "add_address.html")

def addresses(request):

    addresses = Address.objects.filter(user=request.user)

    return render(request,"addresses.html",{
        "addresses":addresses
    })