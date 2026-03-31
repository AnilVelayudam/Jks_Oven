from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Order, OrderItem, Address, Review
from .forms import ReviewForm

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Address
from datetime import date, timedelta


from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse

from django.core.mail import send_mail

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
# ================= CHECKOUT =================
from django.contrib.auth.decorators import login_required

@login_required
def checkout(request):

    request.session['user_id'] = request.user.id

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

            # 🔥 remove only selected items
            if selected_keys:
                for key in selected_keys:
                    cart.pop(key, None)
                request.session['cart'] = cart
            else:
                request.session['cart'] = {}

            request.session.pop('buy_now', None)
            request.session.pop('selected_items', None)
            send_mail(
                "Order Confirmed 🧁",
                f"Hi {request.user.username}, your order #{order.id} has been placed successfully!",
                "no-reply@jksoven.com",
                [request.user.email],
                fail_silently=True,
            )

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



from datetime import date

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

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

    return render(request, "order_detail.html", {
        "order": order,
        "eta_message": eta_message
    })

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
@csrf_exempt
def payment_success(request):

    if request.method == "POST":

        payment_id = request.POST.get("razorpay_payment_id")
        user_id = request.POST.get("user_id")
        address_id = request.POST.get("address_id")

        # 🔥 safety check
        if not payment_id or not user_id or not address_id:
            return redirect("checkout")

        if not payment_id.startswith("pay_"):
            return redirect("checkout")

        try:
            user = User.objects.get(id=user_id)
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

            # save items
            for item in items_to_order:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['price']
                )

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

            # ================= EMAIL =================
            send_mail(
                "Payment Successful 🎉",
                f"Hi {user.username}, your payment for order #{order.id} is successful!",
                "no-reply@jksoven.com",
                [user.email],
                fail_silently=True,
            )

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



def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # ⏱ check cancel allowed
    can_cancel = False
    if order.status == "PENDING":
        if timezone.now() - order.created_at <= timedelta(hours=1):
            can_cancel = True

    return render(request, "order_detail.html", {
        "order": order,
        "can_cancel": can_cancel
    })

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