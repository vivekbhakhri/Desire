"""Storefront content: banners, categories, products, taxes, attachments."""
from django.db import models
from django.db.models import Avg, Count
from django.urls import reverse
from tinymce.models import HTMLField

from core.constants import LABEL_CHOICES, TAX_VALUE_TYPES
from core.validators import validate_file_size

from .accounts import Profile


class HomeImage(models.Model):
    main_title = models.CharField(max_length=1000, null=True, blank=True)
    badge_title = models.CharField(max_length=1000, null=True, blank=True)
    image = models.ImageField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Banner"

    def __str__(self):
        return f"{self.main_title} {self.is_active}"


class Slide(models.Model):
    caption1 = models.CharField(max_length=100)
    caption2 = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    image = models.ImageField(help_text="Size: 1920x570")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.caption1} - {self.caption2}"


class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255)
    description = models.TextField()
    image = models.ImageField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("shop:product", kwargs={"slug": self.slug, "id": self.id})


class Tax(models.Model):
    categoryId = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.CASCADE
    )
    TaxName = models.CharField(max_length=50)
    ValueType = models.CharField(choices=TAX_VALUE_TYPES, max_length=50)
    TaxValue = models.FloatField()


class Item(models.Model):
    unique_id = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Item Id"
    )
    seller = models.ForeignKey(Profile, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name="Item Name")
    price = models.FloatField()
    brandName = models.CharField(max_length=255, null=True, blank=True)
    discount_price = models.FloatField(blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True
    )
    label = models.CharField(choices=LABEL_CHOICES, max_length=50)
    slug = models.SlugField(max_length=255)
    stock_no = models.CharField(max_length=10)
    description_short = HTMLField(blank=True, verbose_name="Product Description")
    description_long = HTMLField(blank=True, verbose_name="Shipping Details")
    image = models.ImageField()
    is_active = models.BooleanField(default=True)
    has_variations = models.BooleanField(default=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Products"

    def __str__(self):
        return self.unique_id or str(self.pk)

    def get_absolute_url(self):
        return reverse("shop:productpage", kwargs={"slug": self.slug, "id": self.id})

    def get_add_to_cart_url(self):
        return reverse("shop:addItemToCart", kwargs={"id": self.id, "qt": 1})

    def get_remove_from_cart_url(self):
        return reverse("shop:removeFromCart", kwargs={"id": self.id})

    def avaregereview(self) -> float:
        from .content import Comment

        agg = Comment.objects.filter(product=self, status="True").aggregate(
            avarage=Avg("rate")
        )
        return float(agg["avarage"] or 0)

    def countreview(self) -> int:
        from .content import Comment

        agg = Comment.objects.filter(product=self, status="True").aggregate(
            count=Count("id")
        )
        return int(agg["count"] or 0)

    def get_attachments(self):
        return Attachment.objects.filter(productId=self.id)


class Attachment(models.Model):
    productId = models.ForeignKey(Item, on_delete=models.CASCADE)
    media_attach = models.FileField(
        blank=True, null=True, validators=[validate_file_size]
    )

    def __str__(self):
        return f"{self.productId} {self.media_attach}"
