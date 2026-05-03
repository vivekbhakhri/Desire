"""Application forms.

Note: `CommentForm` and `ContactForm` previously lived inside `core/models.py`
purely for legacy reasons. They are model-bound forms and belong here.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from tinymce.widgets import TinyMCE

from core.constants import PAYMENT_CHOICES


# ---------------------------------------------------------------------------
# File upload widgets
# ---------------------------------------------------------------------------
# Django 5 forbids `ClearableFileInput(multiple=True)`; the supported pattern
# is a custom widget + field pair.

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single = super().clean
        if isinstance(data, (list, tuple)):
            return [single(d, initial) for d in data]
        return single(data, initial)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class CreateUserForm(UserCreationForm):
    contact_number = forms.CharField(max_length=255)
    alt_contact_number = forms.CharField(max_length=255, required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
            "first_name",
            "contact_number",
            "alt_contact_number",
        )

    def clean_contact_number(self):
        contact_number = self.cleaned_data["contact_number"]
        if len(contact_number) != 8 or int(contact_number[0]) < 6:
            raise ValidationError("Please enter a correct number!")
        return contact_number


class UserLogInForm(forms.Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput())


class ServiceLogInForm(forms.Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput())


# ---------------------------------------------------------------------------
# Catalog / checkout
# ---------------------------------------------------------------------------

class CreateProductForm(forms.Form):
    Product_Description = forms.CharField(
        widget=TinyMCE(attrs={"class": "col-lg-8 col-sm-12 form"})
    )
    Shipping_Details = forms.CharField(
        widget=TinyMCE(attrs={"class": "col-lg-8 col-sm-12 form"})
    )


class FileUploadForm(forms.Form):
    files = MultipleFileField()


class RadioCheckoutForm(forms.Form):
    payment_option = forms.CharField(
        widget=forms.RadioSelect(
            choices=PAYMENT_CHOICES, attrs={"class": "my-radio"}
        )
    )


# ---------------------------------------------------------------------------
# Model-bound forms
# ---------------------------------------------------------------------------

from core.models.content import Comment, Contact  # noqa: E402  (after widget defs)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["rate"]


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["fname", "lname", "mobileno", "emailId", "subject"]
