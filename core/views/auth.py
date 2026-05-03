"""Customer + service-provider login, registration, logout."""
from __future__ import annotations

import re

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from core.forms import CreateUserForm, ServiceLogInForm, UserLogInForm
from core.models import Category, Profile
from core.services.permissions import is_customer, is_service_provider

# Validation regexes (raw strings — Python 3.12+ raises SyntaxWarning otherwise).
EMAIL_RE = re.compile(r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$")
PASSWORD_RE = re.compile(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])\w{6,}$")


def customer_login_page(request):
    if request.user.is_authenticated:
        return redirect("shop:index")

    form = UserLogInForm()
    if request.method == "POST":
        form = UserLogInForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user and is_customer(user):
                login(request, user)
                messages.success(request, "Logged in as a Customer")
                return redirect("shop:index")
            messages.error(request, "User Id and Password don't match.")
            return redirect("shop:login")

    return render(
        request,
        "customer_login.html",
        {"form": form, "category": Category.objects.filter(is_active=True)},
    )


def service_login_page(request):
    if request.user.is_authenticated:
        return redirect("shop:ordersreceived")

    form = ServiceLogInForm()
    if request.method == "POST":
        form = ServiceLogInForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user and is_service_provider(user):
                login(request, user)
                messages.success(request, "Logged in as a Service Provider")
                return redirect("shop:profile")
            messages.error(request, "User Id and Password don't match.")
            return redirect("shop:service_login_page")

    return render(request, "servicepro_login.html", {"form": form})


@login_required(login_url="shop:index")
def user_logout_page(request):
    logout(request)
    return redirect("shop:index")


def customerregistrtion_page(request):
    return render(request, "customerregistrtion.html")


def _validate_registration(request, *, require_password_strength: bool, redirect_name: str):
    """Returns (is_valid, response_or_data)."""
    fname = request.POST["first_name"]
    password1 = request.POST["password1"]
    password2 = request.POST["password2"]
    phone_no = request.POST["contact_number"]
    email = request.POST["username"]

    if User.objects.filter(email=email).exists():
        messages.error(
            request,
            "Email ID already taken. Do Login If You Are An Existing User",
        )
        return False, redirect(redirect_name)
    if not EMAIL_RE.search(email):
        messages.error(request, "Enter proper email ID")
        return False, redirect(redirect_name)
    if not phone_no or len(phone_no.strip()) < 9:
        messages.error(request, "Please Enter Proper Contact Number.")
        return False, redirect(redirect_name)
    if require_password_strength and not PASSWORD_RE.search(password1):
        messages.error(
            request,
            "Password must be at least six characters with one number, "
            "one lowercase and one uppercase letter",
        )
        return False, redirect(redirect_name)
    if password1 != password2:
        messages.error(request, "Entered Passwords are not same")
        return False, redirect(redirect_name)
    return True, {
        "fname": fname,
        "password": password1,
        "phone": phone_no,
        "email": email,
    }


def registration_page(request, backend="django.contrib.auth.backends.ModelBackend"):
    if request.user.is_authenticated:
        return redirect("shop:index")

    form = CreateUserForm()
    if request.method == "POST":
        ok, payload = _validate_registration(
            request, require_password_strength=True, redirect_name="shop:registration"
        )
        if not ok:
            return payload

        user = User.objects.create_user(
            username=payload["email"],
            email=payload["email"],
            password=payload["password"],
        )
        user.first_name = payload["fname"]
        user.groups.add(1)  # Customers group
        user.save()

        profile = Profile.objects.create(
            user=user,
            contact_number=payload["phone"],
            is_service_provider=False,
            alt_contact_number=request.POST.get("alt_contact_number") or None,
        )
        profile.unique_id = f"C{profile.id}"
        profile.save()

        messages.success(request, "User is Registered Successfully")
        return redirect("shop:login")

    return render(request, "register.html", {"form": form})


def registration_sp_page(request):
    if request.user.is_authenticated:
        return redirect("shop:ordersreceived")

    form = CreateUserForm()
    if request.method == "POST":
        ok, payload = _validate_registration(
            request,
            require_password_strength=False,
            redirect_name="shop:registration_sp",
        )
        if not ok:
            return payload

        user = User.objects.create_user(
            username=payload["email"],
            email=payload["email"],
            password=payload["password"],
        )
        user.first_name = payload["fname"]
        user.groups.add(2)  # Service Providers group
        user.save()

        profile = Profile.objects.create(
            user=user,
            contact_number=payload["phone"],
            is_service_provider=True,
            alt_contact_number=request.POST.get("alt_contact_number") or None,
        )
        profile.unique_id = f"S{profile.id}"
        profile.save()

        messages.success(request, "User is Registered Successfully")
        return redirect("shop:service_login_page")

    return render(request, "register_sp.html", {"form": form})
