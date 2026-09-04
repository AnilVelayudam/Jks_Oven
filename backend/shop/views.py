from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from .models import Product,ProductOption, Order, OrderItem, Address, Review
from .forms import ReviewForm

from django.contrib.auth.decorators import login_required
from .models import Address
from datetime import date, timedelta

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse

from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.contrib import messages
# ================= HOME =================
# ================= HOME =================
def home(request):

    featured_cakes = Product.objects.filter(
        category="cake"
    )[:8]

    famous_items = Product.objects.all()

    # Set display price for every product
    for product in famous_items:

        if product.category == "cake":

            product.display_price = product.whipping_price

        elif product.category == "cookie":

            product.display_price = product.cookie_pack_price

        elif product.options.exists():

            first_option = product.options.order_by("id").first()

            if first_option:
                product.display_price = first_option.price
            else:
                product.display_price = product.price

        else:

            product.display_price = product.price

    return render(request, "home.html", {
        "featured_cakes": featured_cakes,
        "famous_items": famous_items
    })
#

# ============================================================
# ADD TO CART
# ============================================================

def add_to_cart(request, product_id):

    cart = request.session.get("cart", {})
    product = get_object_or_404(Product, id=product_id)

    cream = request.GET.get("cream")
    weight = request.GET.get("weight")
    option_id = request.GET.get("option_id")

    option = None
    option_name = None
    final_price = None
    cart_key = None

    # ============================================================
    # CAKE
    # ============================================================

    if product.category == "cake":

        if not cream or not weight:
            return redirect(
                "product_detail",
                product_id=product_id
            )

        if cream == "whipping":
            base_price = product.whipping_price

        elif cream == "butter":
            base_price = product.buttercream_price

        else:
            return redirect(
                "product_detail",
                product_id=product_id
            )

        if base_price is None:
            return redirect(
                "product_detail",
                product_id=product_id
            )

        try:
            weight_decimal = Decimal(str(weight))
        except (TypeError, ValueError):
            return redirect(
                "product_detail",
                product_id=product_id
            )

        if weight_decimal <= 0:
            return redirect(
                "product_detail",
                product_id=product_id
            )

        # Unit price for this cake
        final_price = Decimal(str(base_price)) * weight_decimal

        # Same cake + cream + weight = same cart item
        cart_key = (
            f"{product_id}_cake_{cream}_{weight}"
        )

    # ============================================================
    # DYNAMIC PRODUCT OPTIONS
    #
    # Example:
    #
    # Donut - 1  = ₹10
    # Donut - 2  = ₹20
    # Donut - 6  = ₹55
    #
    # IMPORTANT:
    # Option itself decides the UNIT PRICE.
    # Cart quantity is separate.
    # ============================================================

    elif option_id:

        try:
            option = ProductOption.objects.get(
                id=int(option_id),
                product=product
            )

        except (
            ProductOption.DoesNotExist,
            ValueError,
            TypeError
        ):
            return redirect(
                "product_detail",
                product_id=product_id
            )

        if option.price is None:
            return redirect(
                "product_detail",
                product_id=product_id
            )

        option_name = option.option_name

        # IMPORTANT:
        # This is the UNIT PRICE.
        #
        # Example:
        # Donut option 6 = ₹55
        #
        # Quantity 1 -> ₹55
        # Quantity 2 -> ₹55 each
        # Quantity 3 -> ₹55 each

        final_price = Decimal(str(option.price))

        # IMPORTANT:
        # Same option gets the same cart key.
        #
        # Donut option 6:
        # 35_option_3
        #
        # Adding it again increases quantity
        # instead of creating another row.

        cart_key = (
            f"{product_id}_option_{option.id}"
        )

    # ============================================================
    # COOKIE
    # ============================================================

    elif product.category == "cookie":

        if product.cookie_pack_price is None:
            return redirect(
                "product_detail",
                product_id=product_id
            )

        # Cookie pack UNIT PRICE
        final_price = Decimal(
            str(product.cookie_pack_price)
        )

        # Same cookie pack = same cart item
        cart_key = f"{product_id}_cookie"

    # ============================================================
    # NORMAL PRODUCT
    # ============================================================

    else:

        if product.price is None:
            return redirect(
                "product_detail",
                product_id=product_id
            )

        # Normal product UNIT PRICE
        final_price = Decimal(
            str(product.price)
        )

        cart_key = f"{product_id}_simple"

    # ============================================================
    # EXISTING CART ITEM
    # ============================================================

    if cart_key in cart:

        # Only increase quantity.
        #
        # DO NOT multiply price here.
        # DO NOT change price based on quantity.

        old_quantity = int(
            cart[cart_key].get("quantity", 0)
        )

        cart[cart_key]["quantity"] = old_quantity + 1

        # Keep UNIT PRICE exactly the same.
        cart[cart_key]["price"] = float(final_price)

    # ============================================================
    # NEW CART ITEM
    # ============================================================

    else:

        cart[cart_key] = {
            "product_id": product_id,

            # Cake information
            "cream": cream,
            "weight": weight,

            # Product option information
            "option_id": (
                option.id
                if option
                else None
            ),

            "option_name": option_name,

            # IMPORTANT:
            # This is UNIT PRICE only.
            "price": float(final_price),

            # Start with quantity 1
            "quantity": 1,
        }

    # ============================================================
    # SAVE CART
    # ============================================================

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


# ============================================================
# CART VIEW
# ============================================================

def cart_view(request):

    cart = request.session.get("cart", {})

    cart_items = []
    total = Decimal("0.00")

    for key, item in cart.items():

        # Ignore invalid session data
        if not isinstance(item, dict):
            continue

        product_id = item.get("product_id")

        if not product_id:
            continue

        product = Product.objects.filter(
            id=product_id
        ).first()

        if not product:
            continue

        # ========================================================
        # QUANTITY
        # ========================================================

        try:
            quantity = int(
                item.get("quantity", 1)
            )
        except (TypeError, ValueError):
            quantity = 1

        if quantity < 1:
            quantity = 1

        # ========================================================
        # UNIT PRICE
        # ========================================================

        try:
            price = Decimal(
                str(item.get("price", 0))
            )
        except (TypeError, ValueError):
            price = Decimal("0.00")

        # ========================================================
        # SUBTOTAL
        #
        # Example:
        #
        # Option 6 = ₹55
        # Quantity = 2
        #
        # 55 × 2 = ₹110
        # ========================================================

        subtotal = price * quantity

        total += subtotal

        # ========================================================
        # CART ITEM
        # ========================================================

        cart_items.append({
            "key": key,

            "product": product,

            # Quantity
            "quantity": quantity,

            # UNIT PRICE
            "price": price,

            # TOTAL FOR THIS ITEM
            "subtotal": subtotal,

            # Cake
            "cream": item.get("cream"),
            "weight": item.get("weight"),

            # Dynamic option
            "option_id": item.get("option_id"),
            "option_name": item.get("option_name"),
        })

    return render(
        request,
        "cart.html",
        {
            "cart_items": cart_items,
            "total": total,
        }
    )


# ============================================================
# INCREASE QUANTITY
# ============================================================

def increase_quantity(request, key):

    cart = request.session.get("cart", {})

    if key in cart:

        try:
            current_quantity = int(
                cart[key].get("quantity", 1)
            )
        except (TypeError, ValueError):
            current_quantity = 1

        cart[key]["quantity"] = (
            current_quantity + 1
        )

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


# ============================================================
# DECREASE QUANTITY
# ============================================================

def decrease_quantity(request, key):

    cart = request.session.get("cart", {})

    if key in cart:

        try:
            current_quantity = int(
                cart[key].get("quantity", 1)
            )
        except (TypeError, ValueError):
            current_quantity = 1

        current_quantity -= 1

        if current_quantity <= 0:

            del cart[key]

        else:

            cart[key]["quantity"] = current_quantity

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


# ============================================================
# REMOVE FROM CART
# ============================================================

def remove_from_cart(request, key):

    cart = request.session.get("cart", {})

    if key in cart:
        del cart[key]

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


# ================= CART VIEW =================
def cart_view(request):

    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for key, item in cart.items():

        # Skip invalid cart data
        if not isinstance(item, dict):
            continue

        product = Product.objects.filter(
            id=item.get('product_id')
        ).first()

        if not product:
            continue

        quantity = item.get('quantity', 1)
        price = item.get('price', 0)

        subtotal = price * quantity
        total += subtotal

        cart_items.append({
            'key': key,
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
            'price': price,

            # Cake data
            'cream': item.get('cream'),
            'weight': item.get('weight'),

            # Dynamic product option data
            'option_id': item.get('option_id'),
            'option_name': item.get('option_name'),
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
from django.contrib.auth.decorators import login_required

@login_required
def checkout(request):

    cart = request.session.get('cart', {})
    buy_now = request.session.get('buy_now')

    cart_items = []
    total = 0

    # 🔥 STEP 1: get selected items (POST or SESSION)
    selected_keys = request.POST.getlist("selected_items")

    if not selected_keys:
        selected_keys = request.session.get("selected_items", [])

    # ================= SELECTED ITEMS =================
    if selected_keys:

        for key, item in cart.items():

            if key not in selected_keys:
                continue

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

    # ================= BUY NOW =================
    elif buy_now:

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

    # ================= FULL CART =================
    else:

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

    # ================= POST =================
    if request.method == "POST":

        # 🔥 SAVE selected items (IMPORTANT FIX)
        request.session['selected_items'] = selected_keys

        address_id = request.POST.get("address_id")
        request.session['address_id'] = address_id
        payment_method = request.POST.get("payment_method")

        if not address_id:
            return render(request, "checkout.html", {
                "total": total,
                "addresses": addresses,
                "cart_items": cart_items,
                "error": "Please select an address"
            })

        address = Address.objects.get(id=address_id)

        # ================= COD =================
        if payment_method == "cod":
            eta = date.today() + timedelta(days=3)

            order = Order.objects.create(
                user=request.user,
                total_amount=total,
                address=address,
                status="PENDING",
                payment_method="COD",
                payment_status="PENDING",
                estimated_delivery=eta
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['price']
                )
                    # ✅ ADD EMAIL HERE
            import threading
            threading.Thread(
                target=send_order_email,
                args=(request.user, order)
            ).start()

            # 🔥 remove only selected items
            if selected_keys:
                for key in selected_keys:
                    cart.pop(key, None)
                request.session['cart'] = cart
            else:
                request.session['cart'] = {}

            request.session.pop('buy_now', None)
            request.session.pop('selected_items', None)


            return redirect(f"/order-success/?order_id={order.id}")

        # ================= RAZORPAY =================
        else:
            import razorpay
            from django.conf import settings

            client = razorpay.Client(auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            ))

            payment = client.order.create({
                "amount": int(total * 100),
                "currency": "INR",
                "payment_capture": 1
            })

            return render(request, "checkout.html", {
                "total": total,
                "addresses": addresses,
                "cart_items": cart_items,
                "razorpay_order_id": payment['id'],
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "amount": total,
                "open_payment": True,
                "selected_address": address_id
            })

    # ================= GET =================
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

# ================= Forgot password =================
from django.contrib.auth.hashers import make_password

# def forgot_password(request):
#     if request.method == "POST":
#         email = request.POST.get("email")

#         try:
#             user = User.objects.get(email=email)

#             # 🔥 TEMP: direct reset link (no email for now)
#             return redirect("reset_password", user_id=user.id)

#         except User.DoesNotExist:
#             messages.error(request, "Email not registered")
#             return render(request, "forgot_password.html")

#     return render(request, "forgot_password.html")

# def reset_password(request, user_id):
#     user = User.objects.get(id=user_id)

#     if request.method == "POST":
#         password = request.POST.get("password")
#         confirm = request.POST.get("confirm_password")

#         if password != confirm:
#             messages.error(request, "Passwords do not match")
#             return render(request, "reset_password.html")

#         if len(password) < 6:
#             messages.error(request, "Password too short")
#             return render(request, "reset_password.html")

#         user.password = make_password(password)
#         user.save()

#         messages.success(request, "Password updated successfully!")
#         return redirect("login")

#     return render(request, "reset_password.html")

# ================= REGISTER =================
from django.contrib import messages
import re

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # 🔴 Username exists check
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, "register.html")

        # 🔴 Email exists check
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, "register.html")

        # 🔴 Password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, "register.html")

        # 🔴 Password strength check
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters")
            return render(request, "register.html")

        if not re.search(r"[A-Z]", password):
            messages.error(request, "Password must contain at least 1 uppercase letter")
            return render(request, "register.html")

        if not re.search(r"[0-9]", password):
            messages.error(request, "Password must contain at least 1 number")
            return render(request, "register.html")

        # ✅ Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)
        return redirect("home")

    return render(request, "register.html")



# ================= Login DETAIL ================
def login_view(request):
    next_url = request.GET.get("next")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if next_url:
                return redirect(next_url)

            return redirect("profile")

        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")

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
    if request.method == "POST":
        product = Product.objects.get(id=product_id)

        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        # 🔥 GET IMAGE
        image = request.FILES.get('image')

        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment,
            image=image   # 🔥 SAVE IMAGE
        )

        return redirect('product_detail', product_id=product_id)

# ================= SWEET HUB =================
def sweet_hub(request):

    query = request.GET.get('q')

    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    # Display price
    for product in products:

        if product.category == "cake":
            product.display_price = product.whipping_price

        elif product.category == "cookie":
            product.display_price = product.cookie_pack_price

        elif product.options.exists():
            first_option = product.options.order_by("id").first()

            if first_option:
                product.display_price = first_option.price
            else:
                product.display_price = product.price

        else:
            product.display_price = product.price

    # Category names
    category_names = {
        "cake": "Cakes",
        "cookie": "Cookies",
        "brownie": "Brownies",
        "cheesecake": "Cheese Cakes",
        "jarcake": "Jar Cakes",
        "cinnamonroll": "Cinnamon Rolls",
        "donut": "Donuts",
        "bomboloni": "Bomboloni",
        "tiramisu": "Tiramisu",
        "cupcakes": "Cup Cakes",
        "muffins": "Muffins",
        "tresleches": "Tres Leches",
        "icecream": "Ice Cream",
    }

    categories = []

    for code, name in category_names.items():

        first_product = Product.objects.filter(
            category=code
        ).first()

        if first_product:
            categories.append({
                "code": code,
                "name": name,
                "image": first_product.image,
            })

    return render(request, 'sweet_hub.html', {
        'products': products,
        'categories': categories,
    })
# ================= CATEGORY =================
def category_products(request, category):

    products = Product.objects.filter(category=category)

    # Set display price
    for product in products:

        if product.category == "cake":
            product.display_price = product.whipping_price

        elif product.category == "cookie":
            product.display_price = product.cookie_pack_price

        elif product.options.exists():
            first_option = product.options.order_by("id").first()

            if first_option:
                product.display_price = first_option.price
            else:
                product.display_price = product.price

        else:
            product.display_price = product.price

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
    order_id = request.GET.get("order_id")

    order = None
    if order_id:
        order = Order.objects.filter(id=order_id).first()

    return render(request, 'order_success.html', {
        "order": order
    })

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

# ================= EDIT ADDRESS =================
@login_required
def edit_address(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)

    if request.method == "POST":
        address.full_name = request.POST.get("full_name")
        address.phone = request.POST.get("phone")
        address.pincode = request.POST.get("pincode")
        address.house = request.POST.get("house")
        address.area = request.POST.get("area")
        address.landmark = request.POST.get("landmark")
        address.city = request.POST.get("city")
        address.state = request.POST.get("state")

        address.save()
        return redirect("checkout")

    return render(request, "add_address.html", {
        "address": address   # 🔥 send existing data
    })
# ================= DELETE ADDRESS =================
@login_required
def delete_address(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)
    address.delete()
    return redirect("checkout")

# ================= buy now =================

# ================= BUY NOW =================

# ================= BUY NOW =================

@login_required
def buy_now(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    cream = request.GET.get("cream")
    weight = request.GET.get("weight")
    option_id = request.GET.get("option_id")

    option = None


    # ==================================================
    # CAKE
    # ==================================================

    if product.category == "cake":

        if not cream or not weight:

            return redirect(
                'product_detail',
                product_id=product_id
            )


        if cream == "whipping":

            base_price = product.whipping_price

        elif cream == "butter":

            base_price = product.buttercream_price

        else:

            return redirect(
                'product_detail',
                product_id=product_id
            )


        if base_price is None:

            return redirect(
                'product_detail',
                product_id=product_id
            )


        try:

            weight_decimal = Decimal(
                str(weight)
            )

        except (
            TypeError,
            ValueError,
            ArithmeticError
        ):

            return redirect(
                'product_detail',
                product_id=product_id
            )


        final_price = (
            base_price *
            weight_decimal
        )



    # ==================================================
    # PRODUCT OPTION
    # ==================================================

    elif option_id:

        try:

            option = ProductOption.objects.get(
                id=int(option_id),
                product=product
            )

        except (
            ProductOption.DoesNotExist,
            ValueError,
            TypeError
        ):

            return redirect(
                'product_detail',
                product_id=product_id
            )


        if option.price is None:

            return redirect(
                'product_detail',
                product_id=product_id
            )


        try:

            final_price = Decimal(
                str(option.price)
            )

        except (
            TypeError,
            ValueError,
            ArithmeticError
        ):

            return redirect(
                'product_detail',
                product_id=product_id
            )



    # ==================================================
    # COOKIE
    # ==================================================

    elif product.category == "cookie":

        final_price = (
            product.cookie_pack_price
        )


        if final_price is None:

            return redirect(
                'product_detail',
                product_id=product_id
            )


        final_price = Decimal(
            str(final_price)
        )



    # ==================================================
    # NORMAL PRODUCT
    # ==================================================

    else:

        final_price = product.price


        if final_price is None:

            return redirect(
                'product_detail',
                product_id=product_id
            )


        final_price = Decimal(
            str(final_price)
        )



    # ==================================================
    # BUY NOW SESSION
    # ==================================================

    request.session['buy_now'] = {

        'product_id': product.id,

        'cream': cream,

        'weight': weight,

        'option_id': option_id,

        'option_name': (
            option.option_name
            if option
            else None
        ),

        'price': float(
            final_price
        ),

        'quantity': 1
    }


    request.session.modified = True


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



from datetime import date
from django.utils import timezone
from datetime import date, timedelta

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # ✅ ETA LOGIC
    eta_message = ""

    if order.estimated_delivery:
        today = date.today()
        diff = (order.estimated_delivery - today).days

        if order.status == "DELIVERED":
            eta_message = "🎉 Delivered"
        elif order.status == "CANCELLED":
            eta_message = "❌ Cancelled"
        elif diff == 0:
            eta_message = "📦 Arriving Today"
        elif diff == 1:
            eta_message = "📦 Arriving Tomorrow"
        elif diff > 1:
            eta_message = f"📦 Arriving in {diff} days"
        else:
            eta_message = "📦 On the way"
    else:
        eta_message = "📦 Delivery date not available"

    # ✅ CANCEL TIMER LOGIC
    can_cancel = False
    if order.status == "PENDING":
        if timezone.now() - order.created_at <= timedelta(hours=1):
            can_cancel = True

    return render(request, "order_detail.html", {
        "order": order,
        "eta_message": eta_message,
        "can_cancel": can_cancel
    })



from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from datetime import date, timedelta
import threading

# 🔥 NON-BLOCKING EMAIL
def send_order_email(user, order):
    try:
        items = order.items.all()

        product_list = ""
        for item in items:
            product_list += f"- {item.product.name} (x{item.quantity}) - ₹{item.price}\n"

        # ✅ PAYMENT TYPE
        if order.payment_method == "COD":
            payment_msg = f"Payment Method: Cash on Delivery 💵\nPlease keep ₹{order.total_amount} ready at delivery."
        else:
            payment_msg = "Payment Method: Paid Online ✅"

        subject = f"JKS Oven 🍰 | Order #{order.id} Confirmed"

        message = f"""
Hi {user.username},

🎉 Your order has been placed successfully!

🧾 Order ID: #{order.id}

🛍️ Items:
{product_list}

💰 Total Amount: ₹{order.total_amount}

🚚 Estimated Delivery: {order.estimated_delivery}

💳 {payment_msg}

---------------------------------------
Thank you for ordering from JKS Oven ❤️
Enjoy your delicious treats!

- JKS Oven Team
"""

        send_mail(
            subject,
            message,
            "no-reply@jksoven.com",
            [user.email],
            fail_silently=True,
        )

    except Exception as e:
        print("Email error:", e)
@csrf_exempt
def payment_success(request):

    if request.method == "POST":

        payment_id = request.POST.get("razorpay_payment_id")
        address_id = request.POST.get("address_id")

        # ✅ AUTH CHECK
        if not request.user.is_authenticated:
            return redirect("login")

        user = request.user

        # ✅ VALIDATION
        if not payment_id or not address_id:
            return redirect("checkout")

        if not payment_id.startswith("pay_"):
            return redirect("checkout")

        try:
            address = Address.objects.get(id=address_id)

            cart = request.session.get('cart', {})
            selected_keys = request.session.get('selected_items', [])
            buy_now = request.session.get('buy_now')

            total = 0
            items_to_order = []

            # ================= BUY NOW =================
            if buy_now:
                product = Product.objects.get(id=buy_now['product_id'])

                subtotal = buy_now['price'] * buy_now['quantity']
                total += subtotal

                items_to_order.append({
                    "product": product,
                    "quantity": buy_now['quantity'],
                    "price": buy_now['price']
                })

            # ================= SELECTED ITEMS =================
            elif selected_keys:
                for key in selected_keys:
                    item = cart.get(key)
                    if not item:
                        continue

                    product = Product.objects.get(id=item['product_id'])

                    subtotal = item['price'] * item['quantity']
                    total += subtotal

                    items_to_order.append({
                        "product": product,
                        "quantity": item['quantity'],
                        "price": item['price']
                    })

            # ================= FULL CART =================
            else:
                for key, item in cart.items():
                    product = Product.objects.get(id=item['product_id'])

                    subtotal = item['price'] * item['quantity']
                    total += subtotal

                    items_to_order.append({
                        "product": product,
                        "quantity": item['quantity'],
                        "price": item['price']
                    })

            # ================= CREATE ORDER =================
            eta = date.today() + timedelta(days=3)

            order = Order.objects.create(
                user=user,
                total_amount=total,
                address=address,
                status="PENDING",
                payment_method="ONLINE",
                payment_status="PAID",
                payment_id=payment_id,
                estimated_delivery=eta
            )


            # ================= SAVE ITEMS =================
            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['price']
                ) for item in items_to_order
            ])

            # ================= REMOVE ITEMS =================
            if selected_keys:
                for key in selected_keys:
                    cart.pop(key, None)
                request.session['cart'] = cart
            else:
                request.session['cart'] = {}

            # ================= CLEAN SESSION =================
            request.session.pop('selected_items', None)
            request.session.pop('buy_now', None)

            # 🔥 NON-BLOCKING EMAIL (FIX DELAY)
            threading.Thread(
                target=send_order_email,
                args=(user, order)
            ).start()

            # ✅ FAST REDIRECT
            return redirect(f"/order-success/?order_id={order.id}")

        except Exception as e:
            print("ERROR:", e)
            return redirect("checkout")

    return redirect("checkout")

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from datetime import timedelta
from django.utils import timezone
import razorpay
from django.conf import settings
@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if timezone.now() - order.created_at <= timedelta(hours=1):

        if order.status == "PENDING":

            order.status = "CANCELLED"

            # 💸 REAL REFUND
            if order.payment_method == "ONLINE" and order.payment_id:

                try:
                    client = razorpay.Client(auth=(
                        settings.RAZORPAY_KEY_ID,
                        settings.RAZORPAY_KEY_SECRET
                    ))

                    client.payment.refund(order.payment_id)

                    order.payment_status = "REFUNDED"

                except Exception as e:
                    print("Refund Error:", e)
                    order.payment_status = "FAILED"

            else:
                order.payment_status = "FAILED"

            order.save()

    return redirect("order_detail", order_id=order.id)



def download_invoice(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()

    elements = []

    # Title
    elements.append(Paragraph(f"Invoice - Order #{order.id}", styles['Title']))
    elements.append(Spacer(1, 10))

    # Order Info
    elements.append(Paragraph(f"Date: {order.created_at}", styles['Normal']))
    elements.append(Paragraph(f"Total Amount: ₹{order.total_amount}", styles['Normal']))
    elements.append(Spacer(1, 10))

    # Address
    if order.address:
        elements.append(Paragraph("Delivery Address:", styles['Heading3']))
        elements.append(Paragraph(
            f"{order.address.full_name}, {order.address.house}, "
            f"{order.address.area}, {order.address.city}",
            styles['Normal']
        ))
        elements.append(Spacer(1, 10))

    # Items
    elements.append(Paragraph("Items:", styles['Heading3']))
    for item in order.items.all():
        elements.append(Paragraph(
            f"{item.product.name} - Qty: {item.quantity} - ₹{item.price}",
            styles['Normal']
        ))

    doc.build(elements)
    return response


import razorpay
import hmac
import hashlib
import json
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def razorpay_webhook(request):

    if request.method == "POST":

        body = request.body
        received_signature = request.headers.get("X-Razorpay-Signature")

        # 🔐 verify signature
        generated_signature = hmac.new(
            bytes(settings.RAZORPAY_WEBHOOK_SECRET, 'utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()

        if generated_signature != received_signature:
            return HttpResponse("Invalid signature", status=400)

        data = json.loads(body)

        event = data.get("event")

        # 🎯 PAYMENT SUCCESS
        if event == "payment.captured":

            payment = data["payload"]["payment"]["entity"]
            payment_id = payment["id"]

            try:
                order = Order.objects.get(payment_id=payment_id)

                order.payment_status = "PAID"
                order.save()

            except Order.DoesNotExist:
                pass

        # ❌ PAYMENT FAILED
        elif event == "payment.failed":

            payment = data["payload"]["payment"]["entity"]
            payment_id = payment["id"]

            try:
                order = Order.objects.get(payment_id=payment_id)

                order.payment_status = "FAILED"
                order.save()

            except Order.DoesNotExist:
                pass

        return HttpResponse(status=200)

    return HttpResponse(status=400)