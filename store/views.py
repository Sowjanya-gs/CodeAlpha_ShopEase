
import json
from decimal import Decimal, InvalidOperation

from django.db import models, transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required

from .models import Product, Order, OrderItem, Address, Review


def product_list(request):
    products = Product.objects.all()
    return render(request, "store/product_list.html", {
        "products": products
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    reviews = Review.objects.filter(product=product)

    average_rating = reviews.aggregate(
        average=models.Avg("rating")
    )["average"]

    display_rating = (
        average_rating if average_rating is not None else 4.0
    )

    return render(request, "store/product_detail.html", {
        "product": product,
        "is_authenticated": request.user.is_authenticated,
        "reviews": reviews,
        "average_rating": average_rating,
        "review_count": reviews.count(),
        "display_rating": display_rating,
    })


@login_required
@require_POST
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        rating = int(request.POST.get("rating", 0))
    except (ValueError, TypeError):
        return redirect("product_detail", product_id=product.id)

    comment = request.POST.get("comment", "").strip()

    if rating < 1 or rating > 5 or not comment:
        return redirect("product_detail", product_id=product.id)

    Review.objects.update_or_create(
        product=product,
        user=request.user,
        defaults={
            "rating": rating,
            "comment": comment,
        }
    )

    return redirect("product_detail", product_id=product.id)


def cart(request):
    products = list(
        Product.objects.values(
            "id", "name", "price", "stock", "image_url"
        )
    )
    return render(request, "store/cart.html", {
        "products_json": products
    })


def wishlist(request):
    products = list(
        Product.objects.values(
            "id", "name", "price", "image_url"
        )
    )
    return render(request, "store/wishlist.html", {
        "products": products
    })


def checkout(request):
    products = list(
        Product.objects.values("id", "name", "price", "stock")
    )
    return render(request, "store/checkout.html", {
        "products_json": products
    })


def account(request):
    return render(request, "store/account.html")


def logout_user(request):
    if request.method == "POST":
        logout(request)

    return redirect("product_list")


@login_required(login_url="/login/?tab=login")
def addresses(request):
    user_addresses = Address.objects.filter(
        user=request.user
    ).order_by("-is_default", "-created_at")

    return render(request, "store/addresses.html", {
        "addresses": user_addresses
    })


@login_required(login_url="/login/?tab=login")
@require_POST
def add_address(request):
    full_name = request.POST.get("full_name", "").strip()
    phone = request.POST.get("phone", "").strip()
    address_line = request.POST.get("address_line", "").strip()
    landmark = request.POST.get("landmark", "").strip()
    city = request.POST.get("city", "").strip()
    state = request.POST.get("state", "").strip()
    pin_code = request.POST.get("pin_code", "").strip()
    address_type = request.POST.get("address_type", "Home").strip()
    make_default = request.POST.get("is_default") == "on"

    if not all([
        full_name, phone, address_line,
        city, state, pin_code
    ]):
        return redirect("addresses")

    if (
        len(full_name) > 200
        or len(phone) != 10
        or not phone.isdigit()
        or len(address_line) > 5000
        or len(landmark) > 200
        or len(city) > 100
        or len(state) > 100
        or len(pin_code) != 6
        or not pin_code.isdigit()
        or address_type not in dict(Address.ADDRESS_TYPE_CHOICES)
    ):
        return redirect("addresses")

    with transaction.atomic():
        if make_default or not Address.objects.filter(
            user=request.user
        ).exists():
            Address.objects.filter(
                user=request.user
            ).update(is_default=False)
            make_default = True

        Address.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address_line=address_line,
            landmark=landmark,
            city=city,
            state=state,
            pin_code=pin_code,
            address_type=address_type,
            is_default=make_default,
        )

    return redirect("addresses")


# Save an address directly from the checkout page.
@login_required(login_url="/login/?tab=login")
@require_POST
def save_checkout_address(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "Invalid address data."},
            status=400
        )

    if not isinstance(data, dict):
        return JsonResponse(
            {"error": "Invalid address data."},
            status=400
        )

    full_name = str(data.get("customer_name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    house = str(data.get("house", "")).strip()
    street = str(data.get("street", "")).strip()
    landmark = str(data.get("landmark", "")).strip()
    city = str(data.get("city", "")).strip()
    state = str(data.get("state", "")).strip()
    pin_code = str(data.get("pincode", "")).strip()
    address_type = str(data.get("address_type", "Home")).strip()

    if not all([
        full_name, phone, house, street,
        city, state, pin_code
    ]):
        return JsonResponse(
            {"error": "Please complete all required address details."},
            status=400
        )

    if (
        len(full_name) > 200
        or len(phone) != 10
        or not phone.isdigit()
        or len(house) > 200
        or len(street) > 300
        or len(landmark) > 200
        or len(city) > 100
        or len(state) > 100
        or len(pin_code) != 6
        or not pin_code.isdigit()
        or address_type not in dict(Address.ADDRESS_TYPE_CHOICES)
    ):
        return JsonResponse(
            {"error": "Please enter valid address details."},
            status=400
        )

    address_line = f"{house} {street}".strip()

    with transaction.atomic():
        saved_address = Address.objects.filter(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address_line=address_line,
            city=city,
            state=state,
            pin_code=pin_code,
        ).first()

        if saved_address:
            saved_address.landmark = landmark
            saved_address.address_type = address_type
            saved_address.save(
                update_fields=["landmark", "address_type"]
            )
        else:
            Address.objects.create(
                user=request.user,
                full_name=full_name,
                phone=phone,
                address_line=address_line,
                landmark=landmark,
                city=city,
                state=state,
                pin_code=pin_code,
                address_type=address_type,
                is_default=not Address.objects.filter(
                    user=request.user
                ).exists(),
            )

    return JsonResponse({
        "success": True,
        "message": "Address saved successfully."
    })


@login_required(login_url="/login/?tab=login")
@require_POST
def edit_address(request, address_id):
    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user
    )

    full_name = request.POST.get("full_name", "").strip()
    phone = request.POST.get("phone", "").strip()
    address_line = request.POST.get("address_line", "").strip()
    landmark = request.POST.get("landmark", "").strip()
    city = request.POST.get("city", "").strip()
    state = request.POST.get("state", "").strip()
    pin_code = request.POST.get("pin_code", "").strip()
    address_type = request.POST.get("address_type", "Home").strip()
    make_default = request.POST.get("is_default") == "on"

    if not all([
        full_name, phone, address_line,
        city, state, pin_code
    ]):
        return redirect("addresses")

    if (
        len(full_name) > 200
        or len(phone) != 10
        or not phone.isdigit()
        or len(address_line) > 5000
        or len(landmark) > 200
        or len(city) > 100
        or len(state) > 100
        or len(pin_code) != 6
        or not pin_code.isdigit()
        or address_type not in dict(Address.ADDRESS_TYPE_CHOICES)
    ):
        return redirect("addresses")

    with transaction.atomic():
        if make_default:
            Address.objects.filter(
                user=request.user
            ).update(is_default=False)

        address.full_name = full_name
        address.phone = phone
        address.address_line = address_line
        address.landmark = landmark
        address.city = city
        address.state = state
        address.pin_code = pin_code
        address.address_type = address_type

        if make_default:
            address.is_default = True

        address.save()

    return redirect("addresses")


@login_required(login_url="/login/?tab=login")
@require_POST
def delete_address(request, address_id):
    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user
    )

    was_default = address.is_default
    address.delete()

    if was_default:
        replacement = Address.objects.filter(
            user=request.user
        ).order_by("-created_at").first()

        if replacement:
            replacement.is_default = True
            replacement.save(update_fields=["is_default"])

    return redirect("addresses")


@login_required(login_url="/login/?tab=login")
@require_POST
def set_default_address(request, address_id):
    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user
    )

    with transaction.atomic():
        Address.objects.filter(
            user=request.user
        ).update(is_default=False)

        address.is_default = True
        address.save(update_fields=["is_default"])

    return redirect("addresses")


@login_required(login_url="/login/?tab=login")
def my_orders(request):
    orders = Order.objects.prefetch_related("items").order_by("-created_at")
    return render(request, "store/my_orders.html", {
        "orders": orders
    })


@require_POST
def place_order(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "Invalid request data."},
            status=400
        )

    if not isinstance(data, dict):
        return JsonResponse(
            {"error": "Invalid order data."},
            status=400
        )

    name = str(data.get("customer_name", "")).strip()
    email = str(data.get("email", "")).strip()
    address = str(data.get("address", "")).strip()
    phone = str(data.get("phone", "")).strip()
    payment_method = str(data.get("payment_method", "COD")).strip()
    cart_data = data.get("cart")

    address_details = data.get("address_details", {})

    if not isinstance(address_details, dict):
        return JsonResponse(
            {"error": "Invalid delivery address details."},
            status=400
        )

    house = str(address_details.get("house", "")).strip()
    street = str(address_details.get("street", "")).strip()
    landmark = str(address_details.get("landmark", "")).strip()
    city = str(address_details.get("city", "")).strip()
    state = str(address_details.get("state", "")).strip()
    pin_code = str(address_details.get("pincode", "")).strip()
    address_type = str(
        address_details.get("address_type", "Home")
    ).strip()

    if not all([name, email, address, phone]):
        return JsonResponse(
            {"error": "Please fill in all delivery details."},
            status=400
        )

    if len(name) > 200 or len(email) > 254 or len(address) > 5000:
        return JsonResponse(
            {"error": "One or more details are too long."},
            status=400
        )

    if len(phone) != 10 or not phone.isdigit():
        return JsonResponse(
            {"error": "Enter a valid 10-digit phone number."},
            status=400
        )

    address_line = ""

    if request.user.is_authenticated:
        if not all([house, street, city, state, pin_code]):
            return JsonResponse(
                {"error": "Please complete all required address details."},
                status=400
            )

        if len(pin_code) != 6 or not pin_code.isdigit():
            return JsonResponse(
                {"error": "Enter a valid 6-digit PIN code."},
                status=400
            )

        if (
            len(house) > 200
            or len(street) > 300
            or len(landmark) > 200
            or len(city) > 100
            or len(state) > 100
        ):
            return JsonResponse(
                {"error": "One or more address details are too long."},
                status=400
            )

        if address_type not in dict(Address.ADDRESS_TYPE_CHOICES):
            return JsonResponse(
                {"error": "Select a valid address type."},
                status=400
            )

        address_line = f"{house} {street}".strip()

    if payment_method not in dict(Order.PAYMENT_METHOD_CHOICES):
        return JsonResponse(
            {"error": "Please select a valid payment method."},
            status=400
        )

    if not isinstance(cart_data, dict) or not cart_data:
        return JsonResponse(
            {"error": "Your cart is empty."},
            status=400
        )

    if len(cart_data) > 100:
        return JsonResponse(
            {"error": "Too many products in the cart."},
            status=400
        )

    try:
        with transaction.atomic():
            order_items = []
            total = Decimal("0.00")

            for product_id, raw_quantity in cart_data.items():
                if not str(product_id).isdigit():
                    raise ValueError("Invalid product.")

                if (
                    isinstance(raw_quantity, bool)
                    or not isinstance(raw_quantity, int)
                    or raw_quantity < 1
                ):
                    raise ValueError("Invalid product quantity.")

                product = Product.objects.select_for_update().get(
                    id=int(product_id)
                )

                if raw_quantity > product.stock:
                    raise ValueError(
                        f"Insufficient stock for {product.name}."
                    )

                price = product.price
                subtotal = price * raw_quantity
                total += subtotal

                order_items.append({
                    "product": product,
                    "name": product.name,
                    "price": price,
                    "quantity": raw_quantity,
                    "subtotal": subtotal,
                })

            order = Order.objects.create(
                customer_name=name,
                email=email,
                address=address,
                phone=phone,
                payment_method=payment_method,
                total=total,
                status="Pending",
            )

            for item in order_items:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    product_name=item["name"],
                    product_price=item["price"],
                    quantity=item["quantity"],
                    subtotal=item["subtotal"],
                )

                product = item["product"]
                product.stock -= item["quantity"]
                product.save(update_fields=["stock"])

            # Save the delivery address for logged-in customers.
            if request.user.is_authenticated:
                saved_address = Address.objects.filter(
                    user=request.user,
                    full_name=name,
                    phone=phone,
                    address_line=address_line,
                    city=city,
                    state=state,
                    pin_code=pin_code,
                ).first()

                if saved_address:
                    saved_address.landmark = landmark
                    saved_address.address_type = address_type
                    saved_address.save(
                        update_fields=["landmark", "address_type"]
                    )
                else:
                    Address.objects.create(
                        user=request.user,
                        full_name=name,
                        phone=phone,
                        address_line=address_line,
                        landmark=landmark,
                        city=city,
                        state=state,
                        pin_code=pin_code,
                        address_type=address_type,
                        is_default=not Address.objects.filter(
                            user=request.user
                        ).exists(),
                    )

    except Product.DoesNotExist:
        return JsonResponse(
            {"error": "A product in your cart no longer exists."},
            status=400
        )
    except (ValueError, InvalidOperation) as error:
        return JsonResponse(
            {"error": str(error) or "Invalid order details."},
            status=400
        )

    return JsonResponse({
        "success": True,
        "order_id": order.id,
        "message": "Your order was placed successfully."
    })


def login_signup(request):
    full_name = ""
    email = ""
    message = ""
    active_tab = request.GET.get("tab", "login")

    if request.GET.get("error") == "email_exists":
        message = "An account with this email already exists."
        active_tab = "signup"

    if request.method == "POST":
        form_type = request.POST.get("form_type", "login")

        if form_type == "signup":
            active_tab = "signup"

            full_name = request.POST.get("full_name", "").strip()
            email = request.POST.get("email", "").strip().lower()
            password = request.POST.get("password", "")

            if not full_name or not email or not password:
                message = "Please fill in all fields."

            elif User.objects.filter(email__iexact=email).exists():
                return redirect("/login/?tab=signup&error=email_exists")

            else:
                try:
                    validate_password(password)

                    name_parts = full_name.split()
                    first_name = name_parts[0]
                    last_name = " ".join(name_parts[1:])

                    base_username = email.split("@")[0][:140] or "user"
                    username = base_username
                    counter = 1

                    while User.objects.filter(username=username).exists():
                        username = f"{base_username[:140]}{counter}"
                        counter += 1

                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                    )

                    login(request, user)
                    return redirect("product_list")

                except ValidationError as error:
                    message = " ".join(error.messages)
                    active_tab = "signup"

        else:
            active_tab = "login"

            email = request.POST.get("email", "").strip().lower()
            password = request.POST.get("password", "")

            user_record = User.objects.filter(
                email__iexact=email
            ).first()

            if user_record:
                user = authenticate(
                    request,
                    username=user_record.username,
                    password=password,
                )
            else:
                user = None

            if user is not None:
                login(request, user)
                return redirect("product_list")

            message = "Invalid email or password."

    return render(request, "store/login_signup.html", {
        "message": message,
        "active_tab": active_tab,
        "full_name": full_name,
        "email": email,
    })
