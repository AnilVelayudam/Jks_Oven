from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from decimal import Decimal

from .models import Product, Order, OrderItem, Address, Review
from .forms import ReviewForm


# ================= HOME =================
def home(request):
    featured_cakes = Product.objects.filter(category='cake')[:8]
    famous_items = Product.objects.all()

    return render(request, 'home.html', {
        'featured_cakes': featured_cakes,
        'famous_items': famous_items
    })


# ================= ADD TO CART =================
def add_to_cart(request, product_id):

    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, id=product_id)

    cream = request.GET.get("cream")
    weight = request.GET.get("weight")

    # safety check
    if not cream or not weight:
        return redirect('product_detail', product_id=product_id)

    # price logic
    if cream == "whipping":
        base_price = product.whipping_price
    else:
        base_price = product.buttercream_price

    if not base_price:
        return redirect('product_detail', product_id=product_id)

    weight_decimal = Decimal(weight)
    final_price = base_price * weight_decimal

    cart_key = f"{product_id}_{cream}_{weight}"

    if cart_key in cart:
        cart[cart_key]['quantity'] += 1
    else:
        cart[cart_key] = {
            'product_id': product_id,
            'cream': cream,
            'weight': weight,
            'price': float(final_price),
            'quantity': 1
        }

    request.session['cart'] = cart
    next_page = request.GET.get("next")

    if next_page == "checkout":
        return redirect('checkout')

    return redirect('cart')


# ================= CART VIEW =================
def cart_view(request):

    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for key, item in cart.items():

        # ✅ skip old invalid cart data
        if not isinstance(item, dict):
            continue

        product = Product.objects.filter(id=item['product_id']).first()

        if not product:
            continue

        subtotal = item['price'] * item['quantity']
        total += subtotal

        cart_items.append({
            'key': key,
            'product': product,
            'quantity': item['quantity'],
            'subtotal': subtotal,
            'cream': item['cream'],
            'weight': item['weight'],
            'price': item['price']
        })

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })


# ================= QUANTITY =================
def increase_quantity(request, key):
    cart = request.session.get('cart', {})

    if key in cart:
        cart[key]['quantity'] += 1

    request.session['cart'] = cart
    return redirect('cart')


def decrease_quantity(request, key):
    cart = request.session.get('cart', {})

    if key in cart:
        cart[key]['quantity'] -= 1

        if cart[key]['quantity'] <= 0:
            del cart[key]

    request.session['cart'] = cart
    return redirect('cart')


def remove_from_cart(request, key):
    cart = request.session.get('cart', {})

    if key in cart:
        del cart[key]

    request.session['cart'] = cart
    return redirect('cart')


# ================= CHECKOUT =================
@login_required
def checkout(request):

    buy_now = request.session.get('buy_now')
    cart_items = []
    total = 0

    # 🔥 BUY NOW FLOW
    if buy_now:

        product = Product.objects.filter(id=buy_now['product_id']).first()

        if product:
            subtotal = buy_now['price'] * buy_now['quantity']
            total += subtotal

            cart_items.append({
                'product': product,
                'quantity': buy_now['quantity'],
                'price': buy_now['price'],
                'cream': buy_now['cream'],
                'weight': buy_now['weight']
            })

    # 🛒 NORMAL CART FLOW
    else:

        cart = request.session.get('cart', {})

        for key, item in cart.items():

            if not isinstance(item, dict):
                continue

            product = Product.objects.filter(id=item['product_id']).first()

            if not product:
                continue

            subtotal = item['price'] * item['quantity']
            total += subtotal

            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'price': item['price'],
                'cream': item['cream'],
                'weight': item['weight']
            })

    addresses = Address.objects.filter(user=request.user)

    if request.method == "POST":

        order = Order.objects.create(
            user=request.user,
            total_amount=total
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price']
            )

        if buy_now:
            request.session.pop('buy_now', None)  # ✅ IMPORTANT
        else:
            request.session[cart]={}
        return redirect("order_success")

    return render(request, "checkout.html", {
        "total": total,
        "addresses": addresses,
        "cart_items": cart_items
    })

# ================= PROFILE =================
@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'profile.html', {'orders': orders})


# ================= REGISTER =================
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


# ================= PRODUCT DETAIL =================
def product_detail(request, product_id):

    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)

    return render(request, "product_detail.html", {
        "product": product,
        "reviews": reviews
    })


# ================= ADD REVIEW =================
@login_required
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


# ================= SWEET HUB =================
def sweet_hub(request):

    query = request.GET.get('q')

    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    return render(request, 'sweet_hub.html', {
        'products': products
    })


# ================= CATEGORY =================
def category_products(request, category):

    products = Product.objects.filter(category=category)

    return render(request, "category_products.html", {
        "products": products,
        "category": category
    })


# ================= SEARCH =================
def search_products(request):

    query = request.GET.get('q')
    results = []

    if query:
        products = Product.objects.filter(name__icontains=query)[:5]

        for product in products:
            results.append({
                "id": product.id,
                "name": product.name,
                "price": str(product.whipping_price),
                "image": product.image.url if product.image else ""
            })

    return JsonResponse(results, safe=False)


# ================= ORDER SUCCESS =================
def order_success(request):
    return render(request, 'order_success.html')


# ================= ADDRESS =================
@login_required
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


@login_required
def addresses(request):

    addresses = Address.objects.filter(user=request.user)

    return render(request, "addresses.html", {
        "addresses": addresses
    })



# ================= buy now =================

@login_required
def buy_now(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    cream = request.GET.get("cream")
    weight = request.GET.get("weight")

    if not cream or not weight:
        return redirect('product_detail', product_id=product_id)

    from decimal import Decimal

    if cream == "whipping":
        base_price = product.whipping_price
    else:
        base_price = product.buttercream_price

    if not base_price:
        return redirect('product_detail', product_id=product_id)

    weight_decimal = Decimal(weight)
    final_price = base_price * weight_decimal

    # 🔥 store single product (temporary session)
    request.session['buy_now'] = {
        'product_id': product.id,
        'cream': cream,
        'weight': weight,
        'price': float(final_price),
        'quantity': 1
    }

    return redirect('checkout')


# =================  nbuy_now_from_cart =================
@login_required
def buy_now_from_cart(request, key):

    cart = request.session.get('cart', {})

    item = cart.get(key)

    if not item:
        return redirect('cart')

    # 🔥 move this item to buy_now
    request.session['buy_now'] = item

    return redirect('checkout')