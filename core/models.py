from django.conf import settings
from django.db import models
from django.db.models import Sum,Avg,Count
from django.shortcuts import reverse
from django_countries.fields import CountryField
from django.forms import ModelForm
from tinymce.models import HTMLField
from .validators import validate_file_size
from django.contrib.auth.models import User
from django.contrib.auth.models import User
# Create your models here.


LABEL_CHOICES = (
    ('New', 'New'),
    ('Sale', 'Sale'),
    ('Promotion', 'Promotion'),
)

TAX_VALUE_TYPES = (
    ('In Rupees', 'Rs'),
    ('In Percentage' , 'Percent')
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    #('S', 'Shipping'),
)

ROLES = (
    ('Customer', 'Customer'),
    ('Seller', 'Seller')
)


class HomeImage(models.Model):
    main_title = models.CharField(max_length=1000, null=True, blank=True)
    badge_title = models.CharField(max_length=1000, null=True, blank=True)
    image = models.ImageField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.main_title + " " + str(self.is_active)

    class Meta:
        verbose_name_plural = 'Banner'        

class Subcription(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    price = models.FloatField( null=True, blank=True)
    validity = models.IntegerField(null=True, blank=True)
    entries = models.IntegerField(null=True, blank=True)
    is_booster = models.BooleanField(default=False)
    has_priority_support  = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name + " " +str(self.validity) + " Days"

    class Meta:
        verbose_name_plural = 'Subscription Plans'

# SubscriptionPayment for Graph
class SubscriptionPayment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    price = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Subscription Payments'

class Profile(models.Model):
    unique_id = models.CharField(max_length=255, null=True, blank=True,verbose_name="User Id")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=255)
    alt_contact_number = models.CharField(max_length=255, null=True, blank=True)
    is_service_provider = models.BooleanField(default=False)
    saved = models.BooleanField(default=False)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    address1 = models.CharField(max_length=255, null=True,blank=True)
    address2 = models.CharField(max_length=255, null=True,blank=True)
    state = models.CharField(max_length=255, null=True,blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    zip = models.CharField(max_length=255, null=True, blank=True)
    bank_details_saved = models.BooleanField(default=False)
    account_number = models.CharField(max_length=255, null=True, blank=True)
    ifsc_code = models.CharField(max_length=255, null=True, blank=True)
    account_holder_name = models.CharField(max_length=255, null=True, blank=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    entries_remaining = models.IntegerField(null=True, blank=True, default=0)
    days_valid = models.IntegerField(null=True, blank=True, default=0)
    subcription = models.ForeignKey(Subcription, null=True, blank=True, on_delete=models.CASCADE, limit_choices_to={'is_booster': False})
    booster = models.ForeignKey(Subcription, null=True, blank=True, related_name="+", on_delete=models.CASCADE, limit_choices_to={'is_booster': True})
    subs_date = models.DateTimeField(null=True, blank=True)
    booster_date = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return str(self.unique_id)


class Slide(models.Model):
    caption1 = models.CharField(max_length=100)
    caption2 = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    image = models.ImageField(help_text="Size: 1920x570")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "{} - {}".format(self.caption1, self.caption2)


class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255)
    description = models.TextField()
    image = models.ImageField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:category", kwargs={
            'slug': self.slug
        })
class Tax(models.Model):
    categoryId = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)
    TaxName = models.CharField(max_length=50)
    ValueType = models.CharField(choices=TAX_VALUE_TYPES, max_length=50)
    TaxValue = models.FloatField()

class Item(models.Model):
    unique_id = models.CharField(max_length=255, null=True, blank=True,verbose_name="Item Id")
    seller = models.ForeignKey(Profile, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=100,verbose_name="Item Name")
    price = models.FloatField()
    brandName = models.CharField(max_length=255, null=True, blank=True)
    discount_price = models.FloatField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    label = models.CharField(choices=LABEL_CHOICES, max_length=50)
    slug = models.SlugField(max_length=255)
    stock_no = models.CharField(max_length=10)
    description_short =  HTMLField(blank=True,verbose_name="Product Description")
    # description_long = models.TextField()
    description_long = HTMLField(blank=True,verbose_name="Shipping Details")
    image = models.ImageField()
    is_active = models.BooleanField(default=True)
    has_variations = models.BooleanField(default=True) #This needs to be changed to False before deploying
    # attachments = models.ManyToManyField(Attachment, blank=True, null=True)
    
    state = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return self.unique_id

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })

    def get_id(self):
        return reverse('core:product', kwargs={
            'slug': self.slug,
            'id' : self.id
        })
    def avaregereview(self):
        reviews = Comment.objects.filter(product=self, status='True').aggregate(avarage=Avg('rate'))
        avg=0
        if reviews["avarage"] is not None:
            avg=float(reviews["avarage"])
        return avg

    def countreview(self):
        reviews = Comment.objects.filter(product=self, status='True').aggregate(count=Count('id'))
        cnt=0
        if reviews["count"] is not None:
            cnt = int(reviews["count"])
        return cnt


    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug,
            'qt': 1
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })

    def get_add_to_wish_url(self):
        return reverse("core:add-to-wish", kwargs={
            'slug': self.slug,
            'qt' : 1
        })

    def get_remove_from_wish_url(self):
        return reverse("core:remove-from-wish", kwargs={
            'slug': self.slug
        })

    def get_attachments(self):
        attachments = Attachment.objects.filter(productId=self.id)
        print(attachments)
        return attachments

    class Meta:
        verbose_name_plural = 'Products'



class Attachment(models.Model):
    productId = models.ForeignKey(Item, on_delete=models.CASCADE)
    media_attach = models.FileField(blank=True, null=True,  validators=[validate_file_size])

    def __str__(self):
        return str(self.productId) + " " + str(self.media_attach)


class Comment(models.Model):
    STATUS = (
        ('New', 'New'),
        ('True', 'True'),
        ('False', 'False'),
    )
    unique_id = models.CharField(max_length=255, null=True, blank=True,verbose_name="Comment Id")
    product=models.ForeignKey(Item,on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    subject = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=50, blank=True)
    comment = models.CharField(max_length=250,blank=True)
    rate = models.IntegerField(default=1)
    ip = models.CharField(max_length=20, blank=True)
    status=models.CharField(max_length=10,choices=STATUS, default='False')
    create_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.unique_id
        
    class Meta:
        verbose_name_plural = 'Product Comments'        

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['rate']

class Contact(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, null=True)
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    mobileno = models.IntegerField()
    emailId = models.EmailField(max_length=50)
    subject = models.CharField(max_length=500)
    create_at = models.DateTimeField(auto_now_add=True)
    ip = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return  self.fname + " " + self.lname + " " + self.emailId

class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = ['fname', 'lname', 'mobileno', 'emailId', 'subject']


class OrderItem(models.Model):
    unique_id = models.CharField(max_length=200, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.FloatField(null=True, blank=True) #Variation
    tax = models.FloatField(null=True, blank=True, default=0, verbose_name="Service Charges")
    totalPrice = models.FloatField(null=True, blank=True, default=0)
    ref_code = models.CharField(max_length=20, null=True, blank=True,verbose_name="Reference ID")
    start_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    ordered_date = models.DateTimeField(null=True, blank=True)
    # ordered = models.BooleanField(default=False)
    #shipping_address = models.ForeignKey(
        #'BillingAddress', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'BillingAddress', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Delivery Address")
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    #coupon = models.ForeignKey(
        #'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False, verbose_name="Order Delivered" )
    # received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    order_rejected = models.BooleanField(default=False, verbose_name="Order Cancelled" )
    order_placed = models.BooleanField(default=False, verbose_name="Order Accepted" )
    seller_msg = models.CharField(max_length=1000, null=True, blank=True,verbose_name="Reason")
    
    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        if self.price:
            return self.quantity * self.price
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        if self.price:
            return self.quantity * self.price
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        return self.price

    def getTaxAmount(self):
        tax_num = 0
        for tax in Tax.objects.filter(categoryId=self.item.category):
            if tax.ValueType == "In Rupees":
                tax_num = tax_num + tax.TaxValue
            if tax.ValueType == "In Percentage":
                tax_num = tax_num + float((self.price * tax.TaxValue) / 100.0)
        print(tax_num)
        return tax_num

    class Meta:
        verbose_name_plural = 'Orders Details'

class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    fname = models.CharField(max_length=100,null=True,  blank=True,verbose_name="First Name")
    lname = models.CharField(max_length=100,null=True,  blank=True,verbose_name="Last Name")
    email = models.CharField(max_length=50,null=True,  blank=True,verbose_name="Email Id")
    number = models.CharField(max_length=20, null=True,  blank=True,verbose_name="Phone Number")
    street_address = models.CharField(max_length=100,  blank=True)
    apartment_address = models.CharField(max_length=100,  blank=True)
    #address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100,  null=True,  blank=True)
    state = models.CharField(max_length=100,  null=True,  blank=True)
    zip = models.CharField(max_length=100,  blank=True)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES,  blank=True)
    default = models.BooleanField(default=False)
    country = models.CharField(max_length=1, null=True, blank=True)
    specialInstructions = models.CharField(max_length=1000,  null=True,  blank=True)
    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'BillingAddresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Product Payments'

class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


# class Refund(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE)
#     reason = models.TextField()
#     accepted = models.BooleanField(default=False)
#     email = models.EmailField()

#     def __str__(self):
#         return f"{self.pk}"

class Testimonial(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    role = models.CharField(max_length=100, choices=ROLES, null=True, blank=True)
    testimonial = models.CharField(max_length=1000, null=True, blank=True)
    display = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Contact Us.'

class Seo(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.title
