"""Seller dashboard: products, profile, bank details, subscriptions, orders received."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.utils import timezone

from core.constants import PAYMENT_REDIRECT_HOST
from core.forms import CreateProductForm
from core.models import (
    Attachment,
    Category,
    Item,
    OrderItem,
    Profile,
    Subcription,
    SubscriptionPayment,
)
from core.services.payments import instamojo_client as api
from core.services.payments import razorpay_client as client
from core.services.permissions import (
    has_completed_profile,
    is_service_provider,
)
from core.services.pricing import create_ref_code
from core.services.subscriptions import (
    booster_days,
    has_active_subscription,
    has_remaining_entries,
    order_within_subscription,
    remaining_subscription_days,
)


def _require_complete_profile(request):
    if not has_completed_profile(request.user):
        messages.error(request, "Please Fill the Profile and Bank Details")
        return redirect("shop:profile")
    return None


# ---------------------------------------------------------------------------
# Profile / bank details
# ---------------------------------------------------------------------------

@login_required(login_url="/service-provider-login")
def profile_page(request):
    profile = Profile.objects.filter(user=request.user).first()

    if request.method == "POST" and profile:
        profile.company_name = request.POST["cname"]
        profile.address1 = request.POST["Address1"]
        profile.address2 = request.POST["Address2"]
        profile.state = request.POST["state"]
        profile.city = request.POST["city"]
        profile.zip = request.POST["zip"]
        profile.saved = True
        profile.save()

    user = User.objects.get(username=request.user)
    orders = (
        OrderItem.objects.filter(item__seller=profile, ordered=True)
        if profile
        else []
    )
    return render(
        request,
        "profile.html",
        {"user": user, "profile": profile, "no_orders": len(orders)},
    )


def addbankdetails(request):
    if request.method != "POST":
        return redirect("shop:profile")
    profile = Profile.objects.filter(user=request.user).first()
    if profile:
        profile.account_number = request.POST["account_number"]
        profile.ifsc_code = request.POST["ifsc"]
        profile.account_holder_name = request.POST["account_name"]
        profile.bank_name = request.POST["bank_name"]
        profile.bank_details_saved = True
        profile.save()
    return redirect("shop:profile")


# ---------------------------------------------------------------------------
# Product CRUD
# ---------------------------------------------------------------------------

@login_required(login_url="/service-provider-login")
def addproduct_page(request):
    redirect_response = _require_complete_profile(request)
    if redirect_response:
        return redirect_response

    if not has_active_subscription(request.user):
        messages.error(
            request,
            "You do not have a Subscription to Post Your Products/Services. Subscribe to continue",
        )
        return redirect("shop:subscription")

    if not (remaining_subscription_days(request.user) and has_remaining_entries(request.user)):
        if not has_active_subscription(request.user):
            messages.error(
                request,
                "You do not have a Subscription to Post Your Products/Services. Subscribe to continue",
            )
        if not has_remaining_entries(request.user):
            messages.error(
                request,
                "You have Exhausted the Limit of Your Maximum Entries. Buy a Add-On to Continue",
            )
        return redirect("shop:subscription")

    if request.method == "POST":
        profile = Profile.objects.filter(user=request.user).first()
        category = (
            Category.objects.filter(id=request.POST["category"]).first()
            if request.POST.get("category") not in (None, "0", 0)
            else None
        )

        item = Item.objects.create(
            seller=profile,
            title=request.POST["service_name"],
            price=request.POST["price"],
            discount_price=request.POST["Discount_price"] or False,
            category=category,
            label="New",
            slug=request.POST["service_name"].lower(),
            stock_no=request.POST["stock_number"],
            description_short=request.POST["Product_Description"],
            description_long=request.POST["Shipping_Details"],
            image=request.FILES["upload_image"],
            is_active=True,
            has_variations=False,
            state=request.POST["state"],
            city=request.POST["city"],
            brandName=request.POST["brand_name"],
        )
        item.unique_id = f"S{profile.id}P{item.id}"
        item.save()
        profile.entries_remaining -= 1
        profile.save()

        for f in request.FILES.getlist("files[]"):
            Attachment.objects.create(productId=item, media_attach=f)

        return redirect("shop:serviceproduct")

    return render(
        request,
        "addproduct.html",
        {
            "category": Category.objects.filter(is_active=True),
            "form": CreateProductForm(),
            "profile": Profile.objects.filter(user=request.user).first(),
        },
    )


@login_required(login_url="/service-provider-login")
def updateproduct_page(request, slug, id):
    redirect_response = _require_complete_profile(request)
    if redirect_response:
        return redirect_response

    if request.method == "POST":
        category = (
            Category.objects.filter(id=request.POST["category"]).first()
            if request.POST.get("category") not in (None, "0", 0)
            else None
        )
        item = Item.objects.get(id=id)
        item.title = request.POST["service_name"]
        item.price = request.POST["price"]
        item.discount_price = request.POST["Discount_price"] or False
        item.category = category
        item.slug = request.POST["service_name"].lower()
        item.stock_no = request.POST["stock_number"]
        item.state = request.POST["state"]
        item.city = request.POST["city"]
        item.brandName = request.POST["brand_name"]
        item.description_short = request.POST["Product_Description"]
        item.description_long = request.POST["Shipping_Details"]
        if "upload_image" in request.FILES:
            item.image = request.FILES["upload_image"]
        item.save()

        for f in request.FILES.getlist("files[]"):
            Attachment.objects.create(productId=item, media_attach=f)

        return redirect("shop:serviceproduct")

    item = Item.objects.filter(id=id).first()
    return render(
        request,
        "updateproduct.html",
        {
            "category": Category.objects.filter(is_active=True),
            "form": CreateProductForm(),
            "item": item,
            "attachments": Attachment.objects.filter(productId=item) if item else [],
        },
    )


def deleteItem(request, id):
    profile = Profile.objects.filter(user=request.user).first()
    item = Item.objects.filter(id=id).first()
    if item:
        item.delete()
        if profile:
            profile.entries_remaining += 1
            profile.save()
    return redirect("shop:serviceproduct")


def deleteAttachment(request, id, mainid):
    attachment = Attachment.objects.filter(id=id).first()
    if attachment:
        attachment.delete()
    item = Item.objects.filter(id=mainid).first()
    return render(
        request,
        "updateproduct.html",
        {
            "category": Category.objects.filter(is_active=True),
            "form": CreateProductForm(),
            "item": item,
            "attachments": Attachment.objects.filter(productId=item) if item else [],
        },
    )


# ---------------------------------------------------------------------------
# Seller catalog views
# ---------------------------------------------------------------------------

@login_required(login_url="/service-provider-login")
def serviceproduct_page(request):
    redirect_response = _require_complete_profile(request)
    if redirect_response:
        return redirect_response

    profile = Profile.objects.filter(user=request.user).first()
    context = {}
    if profile:
        context["items"] = Item.objects.filter(seller=profile, is_active=True)
        context["no_orders"] = OrderItem.objects.filter(
            item__seller=profile, ordered=True
        ).count()
    return render(request, "serviceproduct.html", context)


@login_required(login_url="/service-provider-login")
def servicesingleproduct_page(request, slug, id):
    redirect_response = _require_complete_profile(request)
    if redirect_response:
        return redirect_response

    item = Item.objects.filter(id=id).first()
    context = {}
    if item:
        from core.models import Comment

        context["item"] = item
        attachments = Attachment.objects.filter(productId=item)
        if attachments.exists():
            context["attachment"] = attachments
        comments = Comment.objects.filter(product=item, status="True")
        if comments.exists():
            context["comment"] = comments
    return render(request, "servicesingleproduct.html", context)


# ---------------------------------------------------------------------------
# Orders received
# ---------------------------------------------------------------------------

@login_required(login_url="/service-provider-login")
def ordersreceived_page(request):
    redirect_response = _require_complete_profile(request)
    if redirect_response:
        return redirect_response

    if not is_service_provider(request.user):
        return redirect("shop:index")

    profile = Profile.objects.filter(user=request.user).first()
    if not profile:
        return render(request, "ordersreceived.html", {})

    orders = OrderItem.objects.filter(item__seller=profile, ordered=True).order_by("-id")

    counts = {
        "totalOrders": orders.count(),
        "ordersPending": 0,
        "ordersAccepted": 0,
        "ordersCancelled": 0,
        "ordersDelivered": 0,
    }
    in_window = []
    for order in orders:
        if order_within_subscription(order, request.user):
            in_window.append(order)
        if not order.order_placed and not order.order_rejected:
            counts["ordersPending"] += 1
        if order.order_placed and not order.being_delivered:
            counts["ordersAccepted"] += 1
        if order.order_rejected:
            counts["ordersCancelled"] += 1
        if order.order_placed and order.being_delivered:
            counts["ordersDelivered"] += 1

    days_left = remaining_subscription_days(request.user)
    page_number = request.GET.get("page") or 1
    visible_orders = list(orders) if days_left > 0 else in_window
    page_obj = Paginator(visible_orders, 10).get_page(page_number)

    return render(
        request,
        "ordersreceived.html",
        {
            "profile": profile,
            "no_orders": orders.count(),
            "subsDate": days_left,
            "displayInfo": days_left > 0,
            "orders": page_obj,
            **counts,
        },
    )


def accept_order(request, id):
    if is_service_provider(request.user):
        OrderItem.objects.filter(id=id).update(order_placed=True)
    return redirect("shop:ordersreceived")


def decline_order(request):
    if request.method != "POST":
        return redirect("shop:ordersreceived")
    try:
        order_id = request.POST["data"]
        msg = request.POST["msg"]
    except KeyError:
        messages.error(request, "Could not cancel the order. ")
        return redirect("shop:ordersreceived")
    if is_service_provider(request.user):
        OrderItem.objects.filter(id=order_id).update(
            order_rejected=True, seller_msg=msg
        )
    return redirect("shop:ordersreceived")


def delivered_order(request, id):
    if is_service_provider(request.user):
        OrderItem.objects.filter(id=id).update(being_delivered=True)
    return redirect("shop:ordersreceived")


def addMsg(request, id):
    if request.method == "POST":
        order = OrderItem.objects.filter(id=id).first()
        if order and request.POST["msg"]:
            order.seller_msg = request.POST["msg"]
            order.save()
    return redirect("shop:ordersreceived")


# ---------------------------------------------------------------------------
# Subscription purchase flow
# ---------------------------------------------------------------------------

@login_required(login_url="/service-provider-login")
def subscription_page(request):
    redirect_response = _require_complete_profile(request)
    if redirect_response:
        return redirect_response

    subscriptions = Subcription.objects.all()
    context = {
        "subscriptions": subscriptions,
        "has_booster": int(any(s.is_booster for s in subscriptions)),
        "buying": False,
    }

    profile = Profile.objects.filter(user=request.user).first()
    if profile:
        context["no_orders"] = OrderItem.objects.filter(
            item__seller=profile, ordered=True
        ).count()
        if profile.subcription:
            context["mySubs"] = profile.subcription
            if profile.booster:
                context["myBoost"] = profile.booster

    return render(request, "subscription.html", context)


def buySubcription(request, id):
    subscription = Subcription.objects.filter(id=id).first()
    profile = Profile.objects.filter(user=request.user).first()
    if not (subscription and profile):
        return redirect("shop:profile" if profile is None else "shop:subscription")
    if subscription.is_booster and not profile.subcription:
        return redirect("shop:subscription")

    payment_option = request.POST.get("payment_option") if request.method == "POST" else None

    if payment_option == "InstaMojo" and api is not None:
        response = api.payment_request_create(
            amount=subscription.price,
            purpose=f"Buying {subscription.name} Subcription",
            buyer_name=profile,
            redirect_url=f"{PAYMENT_REDIRECT_HOST}/tempView/{subscription.id}/",
        )
        if response["success"]:
            messages.success(request, "Order was successful")
            return redirect(response["payment_request"]["longurl"])
        return redirect("shop:subscription")

    rp = client.order.create(
        {
            "amount": subscription.price * 100,
            "currency": "INR",
            "receipt": create_ref_code(),
        }
    )
    if rp["status"] != "created":
        return redirect("shop:subscription")
    return render(
        request,
        "subscription.html",
        {
            "subs": subscription,
            "DISPLAY_COUPON_FORM": True,
            "buying": True,
            "order_id": rp["id"],
            "price": subscription.price,
            "name": profile.user.username,
            "phone": profile.contact_number,
            "email": profile.user.username,
        },
    )


def _activate_subscription(profile, subscription):
    if subscription.is_booster:
        profile.booster = subscription
        profile.entries_remaining += subscription.entries
        profile.days_valid += subscription.validity
        profile.booster_date = timezone.now()
    else:
        profile.subcription = subscription
        profile.entries_remaining = subscription.entries
        profile.days_valid = subscription.validity + booster_days(profile)
        profile.subs_date = timezone.now()
    profile.save()


def subcription_payment_status(request, id):
    if request.method != "POST":
        return None
    try:
        response = client.order.fetch(request.POST.get("razorpay_order_id"))
        SubscriptionPayment.objects.create(
            user=request.user, price=response["amount"] / 100
        )
        if response["status"] == "paid" and response["amount_due"] == 0:
            profile = Profile.objects.filter(user=request.user).first()
            subscription = Subcription.objects.filter(id=id).first()
            if profile and subscription:
                _activate_subscription(profile, subscription)
            messages.success(
                request, "Your Subscription Plan is Activated Successfully"
            )
            return redirect("shop:profile")
        raise ValueError("Payment not settled")
    except Exception:
        return redirect("shop:subscription")


def tempView(request, id):
    """InstaMojo redirect target after a subscription purchase."""
    payment_id = request.GET.get("payment_id")
    payment_request_id = request.GET.get("payment_request_id")
    if not (payment_id and payment_request_id and api is not None):
        return redirect("shop:subscription")

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
            profile = Profile.objects.filter(user=request.user).first()
            subscription = Subcription.objects.filter(id=id).first()
            if profile and subscription:
                _activate_subscription(profile, subscription)
            return redirect("shop:profile")
    except Exception:
        pass
    return redirect("shop:subscription")
