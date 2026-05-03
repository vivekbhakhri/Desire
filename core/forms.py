from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from tinymce.widgets import TinyMCE

PAYMENT_CHOICES = (
    ("InstaMojo", "Online(Debit/Credit Cards"),
    ("COD", "Cash On Delivery"),
)


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


class CreateProductForm(forms.Form):
    Product_Description = forms.CharField(
        widget=TinyMCE(attrs={"class": "col-lg-8 col-sm-12 form"})
    )
    Shipping_Details = forms.CharField(
        widget=TinyMCE(attrs={"class": "col-lg-8 col-sm-12 form"})
    )


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


class FileUploadForm(forms.Form):
    files = MultipleFileField()


class RadioCheckoutForm(forms.Form):
    payment_option = forms.CharField(
        widget=forms.RadioSelect(
            choices=PAYMENT_CHOICES, attrs={"class": "my-radio"}
        )
    )
