"""User-generated content: comments, contact submissions, testimonials, SEO."""
from django.conf import settings
from django.db import models

from shop.constants import COMMENT_STATUS, ROLES

from .catalog import Item


class Comment(models.Model):
    unique_id = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Comment Id"
    )
    product = models.ForeignKey(Item, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=50, blank=True)
    comment = models.CharField(max_length=250, blank=True)
    rate = models.IntegerField(default=1)
    ip = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=COMMENT_STATUS, default="False")
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Product Comments"

    def __str__(self):
        return self.unique_id or str(self.pk)


class Contact(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    mobileno = models.IntegerField()
    emailId = models.EmailField(max_length=50)
    subject = models.CharField(max_length=500)
    create_at = models.DateTimeField(auto_now_add=True)
    ip = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.fname} {self.lname} {self.emailId}"


class Testimonial(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    role = models.CharField(max_length=100, choices=ROLES, null=True, blank=True)
    testimonial = models.CharField(max_length=1000, null=True, blank=True)
    display = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Contact Us."

    def __str__(self):
        return self.name


class Seo(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.title
