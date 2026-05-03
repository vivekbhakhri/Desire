"""Customer-facing storefront: browsing, cart, checkout, orders, comments."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from core.constants import PAYMENT_REDIRECT_HOST
from core.forms import CommentForm, RadioCheckoutForm
from core.models import (
    Attachment,
    BillingAddress,
    Category,
    Comment,
    HomeImage,
    Item,
    OrderItem,
    Payment,
    Profile,
    Seo,
    Testimonial,
)
from core.services.payments import instamojo_client as api
from core.services.payments import razorpay_client as client
from core.services.pricing import cart_totals, create_ref_code, effective_price


# ---------------------------------------------------------------------------
# Static-ish pages
# ---------------------------------------------------------------------------

def welcome_page(request):
    context = {
        "category": Category.objects.filter(is_active=True),
        "seos": Seo.objects.all(),
        "homeImage": HomeImage.objects.filter(is_active=True),
    }
    if request.user.is_authenticated:
        context["no_orders"] = OrderItem.objects.filter(
            user=request.user, ordered=False
        ).count()
    else:
        context["no_orders"] = 0
    return render(request, "index.html", context)


@login_required
def changepassword_page(request):
    return render(request, "changepassword.html")


@login_required
def confirpasswordmessage_page(request):
    return render(request, "confirmpasswordmessage.html")


@login_required
def forgotpassword_page(request):
    return render(request, "forgotpassword.html")


@login_required
def forgotpasswordmessage_page(request):
    return render(request, "forgotpasswordmessage.html")


def testimonials_page(request):
    if request.method == "POST":
        Testimonial.objects.create(
            name=request.POST["email"],
            role=request.POST.get("role", "Seller"),
            testimonial=request.POST["testimonial"],
        )
        messages.success(
            request, "Thank You for Contacting us we will soon get back to you."
        )
        return redirect("shop:testimonials")

    return render(
        request,
        "testimonials.html",
        {"testimonials": Testimonial.objects.filter(display=True)},
    )


# ---------------------------------------------------------------------------
# Catalog (browsing)
# ---------------------------------------------------------------------------

@login_required(login_url="/login")
def product_page(request, slug, id):
    category = Category.objects.filter(is_active=True)
    my_category = Category.objects.filter(id=id).first()

    context = {
        "id": id,
        "category": category,
        "my_category": my_category,
        "no_orders": OrderItem.objects.filter(
            user=request.user, ordered=False
        ).count(),
    }

    if my_category:
        items = Item.objects.filter(category=my_category, is_active=True)
        paginator = Paginator(items, 45)
        page_number = request.GET.get("page") or 1
        context["orders"] = paginator.get_page(page_number)
        context["currentPage"] = page_number

    return render(request, "product.html", context)


def product_page_json(request, id):
    category = Category.objects.filter(id=id).first()
    if not category:
        return JsonResponse([], safe=False)

    items = Item.objects.filter(category=category, is_active=True)
    page_obj = Paginator(items, 45).get_page(request.GET.get("page") or 1)

    payload = []
    for item in page_obj:
        try:
            priority = bool(
                item.seller.booster.has_priority_support
                or item.seller.subcription.has_priority_support
            )
        except AttributeError:
            priority = False
        payload.append(
            {
                "id": item.id,
                "slug": item.slug,
                "make": item.city,
                "model": item.title,
                "price": str(item.discount_price or item.price),
                "image": item.image.url,
                "type": item.state,
                "priority": priority,
            }
        )
    return JsonResponse(payload, safe=False)


@login_required(login_url="/login")
def productpage_page(request, slug, id):
    item = Item.objects.filter(id=id).first()
    context = {
        "category": Category.objects.filter(is_active=True),
        "no_orders": OrderItem.objects.filter(
            user=request.user, ordered=False
        ).count(),
    }
    if item:
        context["item"] = item
        context["form"] = CommentForm()
        attachments = Attachment.objects.filter(productId=item)
        if attachments.exists():
            context["attachment"] = attachments
        comments = Comment.objects.filter(product=item, status="True")
        if comments.exists():
            context["comment"] = comments
    return render(request, "product-page.html", context)


# ---------------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------------

def _recalculate(cart_item, delta_price):
    """Apply a price delta + recompute tax + grand total in one pass."""
    cart_item.price = (cart_item.price or 0) + delta_price
    cart_item.totalPrice = (cart_item.totalPrice or 0) + delta_price
    cart_item.tax = cart_item.getTaxAmount()
    cart_item.totalPrice = cart_item.price + cart_item.tax
    cart_item.save()


@login_required
def cart_page(request):
    cart = OrderItem.objects.filter(user=request.user, ordered=False)
    context = {
        "object": cart,
        "category": Category.objects.filter(is_active=True),
        "no_orders": cart.count(),
        **cart_totals(cart),
    }
    return render(request, "cart.html", context)


def addItemToCart(request, id, qt):
    item = Item.objects.get(id=id)
    qt = int(qt)
    delta = qt * effective_price(item)

    cart_item = OrderItem.objects.filter(item=item, ordered=False).first()
    if cart_item:
        cart_item.quantity += qt
        _recalculate(cart_item, delta)
    else:
        cart_item = OrderItem.objects.create(
            user=request.user, item=item, quantity=qt, price=delta
        )
        _recalculate(cart_item, 0)
        cart_item.unique_id = f"O{cart_item.id}"
        cart_item.save()
    return redirect("shop:cart")


def removeFromCart(request, id):
    cart_item = OrderItem.objects.filter(id=id).first()
    if cart_item:
        cart_item.delete()
    return redirect("shop:cart")


def removeSingleItem(request, id):
    item = Item.objects.get(id=id)
    cart_item = OrderItem.objects.filter(item=item, ordered=False).first()
    if not cart_item:
        return redirect("shop:cart")

    if cart_item.quantity == 1:
        cart_item.delete()
        return redirect("shop:cart")

    cart_item.quantity -= 1
    _recalculate(cart_item, -effective_price(item))
    return redirect("shop:cart")


# ---------------------------------------------------------------------------
# Checkout / payment
# ---------------------------------------------------------------------------

def _save_billing_address(request) -> BillingAddress:
    address = BillingAddress.objects.create(
        user=request.user,
        fname=request.POST["q2_fullName2[first]"],
        lname=request.POST["q2_fullName2[last]"],
        email=request.POST["q3_email3"],
        street_address=request.POST["q4_billingAddress[addr_line1]"],
        apartment_address=request.POST["q4_billingAddress[addr_line2]"],
        city=request.POST["q4_billingAddress[city]"],
        state=request.POST["q4_billingAddress[state]"],
        zip=request.POST["q4_billingAddress[postal]"],
        address_type="B",
        number=request.POST["q5_contactNumber[full]"],
    )
    notes = request.POST.get("q14_specialInstructions")
    if notes:
        address.specialInstructions = notes
        address.save()
    return address


def _mark_orders_paid(orders, charge_id, ref_code):
    now = timezone.now()
    for item in orders:
        payment = Payment.objects.create(
            stripe_charge_id=charge_id,
            user=item.user,
            amount=item.totalPrice,
        )
        item.ordered = True
        item.payment = payment
        item.ordered_date = now
        item.ref_code = ref_code or create_ref_code()
        item.save()


@login_required
def checkout_page(request):
    if request.method == "POST":
        payment_option = request.POST["payment_option"]
        order_qs = OrderItem.objects.filter(user=request.user, ordered=False)

        if order_qs.exists():
            address = _save_billing_address(request)
            total = 0
            for order in order_qs:
                total += order.totalPrice
                order.billing_address = address
                order.save()

            if payment_option == "InstaMojo" and api is not None:
                response = api.payment_request_create(
                    amount=float(total),
                    purpose="order",
                    buyer_name=User.objects.get(username=request.user),
                    redirect_url=f"{PAYMENT_REDIRECT_HOST}/myorders",
                )
                if response["success"]:
                    messages.success(request, "Order was successful")
                    return redirect(response["payment_request"]["longurl"])

            elif payment_option == "RazorPay":
                rp = client.order.create(
                    {
                        "amount": float(total) * 100,
                        "currency": "INR",
                        "receipt": create_ref_code(),
                    }
                )
                if rp["status"] == "created":
                    context = {
                        "order": order_qs,
                        "DISPLAY_COUPON_FORM": True,
                        "category": Category.objects.filter(is_active=True),
                        "order_id": rp["id"],
                        "price": float(total),
                        "name": address.fname,
                        "phone": address.number,
                        "email": address.email,
                        **cart_totals(order_qs),
                    }
                    return render(request, "checkout.html", context)
                return redirect("shop:checkout")

            elif payment_option == "COD":
                _mark_orders_paid(order_qs, "COD", None)
                return redirect("shop:myorders")

    order = OrderItem.objects.filter(user=request.user, ordered=False)
    context = {"form": RadioCheckoutForm()}
    if order.exists():
        context["order"] = order
        context.update(cart_totals(order))
    return render(request, "checkout.html", context)


def payment_status(request):
    if request.method != "POST":
        return None

    razorpay_order_id = request.POST.get("razorpay_order_id")
    try:
        response = client.order.fetch(razorpay_order_id)
        if response["status"] == "paid" and response["amount_due"] == 0:
            order_qs = OrderItem.objects.filter(user=request.user, ordered=False)
            _mark_orders_paid(order_qs, response["id"], response["receipt"])
        messages.success(request, "Your Order Has been Placed Successfully")
        return redirect("shop:myorders")
    except Exception:
        return redirect("shop:checkout")


# ---------------------------------------------------------------------------
# Customer orders
# ---------------------------------------------------------------------------

@login_required
def myorders_page(request):
    payment_id = request.GET.get("payment_id")
    payment_request_id = request.GET.get("payment_request_id")
    if payment_id and payment_request_id and api is not None:
        try:
            response = api.payment_request_payment_status(
                payment_request_id, payment_id
            )
            request_block = response["payment_request"]
            payment_block = request_block.get("payment", {})
            if (
                request_block["status"] == "Completed"
                and payment_block.get("failure") is None
                and payment_block.get("status") == "Credit"
            ):
                _mark_orders_paid(
                    OrderItem.objects.filter(user=request.user, ordered=False),
                    request_block["id"],
                    None,
                )
        except Exception:
            pass

    open_cart = OrderItem.objects.filter(user=request.user, ordered=False)
    context = {
        "orders": OrderItem.objects.filter(user=request.user, ordered=True).order_by(
            "-id"
        ),
        "category": Category.objects.filter(is_active=True),
        "no_orders": open_cart.count(),
    }
    profile = Profile.objects.filter(user=request.user).first()
    if profile:
        context["profile"] = profile
    return render(request, "myorders.html", context)


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

def addcomment(request, id):
    return_url = request.META.get("HTTP_REFERER", "/")
    if request.method != "POST":
        return HttpResponseRedirect(return_url)

    profile = Profile.objects.filter(user=request.user).first()
    if not profile:
        messages.error(request, "Admin cannot place a comment")
        return HttpResponseRedirect(return_url)

    item = Item.objects.get(id=id)
    comment = Comment.objects.create(
        product=item,
        user=User.objects.get(username=request.user),
        subject=request.POST["name"],
        email=request.POST["email"],
        comment=request.POST["comment"],
        rate=request.POST.get("rating") or 1,
        ip=request.META.get("REMOTE_ADDR", ""),
    )
    comment.unique_id = f"{profile.unique_id}{item.unique_id}Co{comment.id}"
    comment.save()

    messages.success(
        request, "Your review has been sent. Thank you for your interest."
    )
    return HttpResponseRedirect(return_url)
