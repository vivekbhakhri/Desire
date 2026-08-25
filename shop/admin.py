from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from .models import Item, OrderItem, Payment, Coupon, BillingAddress, Category, Slide, Comment, Contact, Attachment, Tax, Profile, Testimonial, Subcription, Seo, HomeImage
from django.contrib.auth.models import User
from django.http import HttpResponse
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.http import JsonResponse
from django.urls import path

# Register your models here.
def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'

class CommentAdmin(admin.ModelAdmin):
    list_display = ['unique_id','comment', 'status','create_at']
    list_filter = ['status']
    fields=('unique_id','product','user','subject','comment','rate','status','ip')
    readonly_fields = ('unique_id','subject','ip','user','product','id')

class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'city',
        'state',
        'zip',
        'address_type'
        
    ]
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']
    readonly_fields = ('user','address_type')


def copy_items(modeladmin, request, queryset):
    for object in queryset:
        object.id = None
        object.save()


copy_items.short_description = 'Copy Items'


class AttachmentInline(admin.StackedInline):
    model = Attachment
    extra = 0
    max_num = 5
class TaxInline(admin.StackedInline):
    model = Tax
    extra = 0
    max_num = 5

class ItemAdmin(admin.ModelAdmin):
    list_display = [
        'unique_id',
        'title',
        'category',
    ]
    list_filter = ['title', 'category']
    search_fields = ['title', 'category']
    prepopulated_fields = {"slug": ("title",)}
    actions = [copy_items]
    inlines = [AttachmentInline]
    help_texts = {'title':'title is displayed here'}
    readonly_fields = ('unique_id','seller',)
    fields=('unique_id','seller','title','price','discount_price','brandName','category','slug','stock_no','description_short','description_long','image','is_active')

class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'is_active'
    ]
    list_filter = ['title', 'is_active']
    search_fields = ['title', 'is_active']
    prepopulated_fields = {"slug": ("title",)}
    inlines = [TaxInline]
    
class PaymentAdmin(admin.ModelAdmin):
    readonly_fields = ('amount','stripe_charge_id','user','timestamp')
    fields=('stripe_charge_id','user','amount','timestamp')
    
class OrderItemAdmin(admin.ModelAdmin):
   # fields = ('id',)
    list_display = [
        'unique_id',
        'ordered',
        'order_placed',
        'being_delivered',
        'order_rejected'
    ]
    readonly_fields = ('unique_id', 'user','item','quantity','price','tax','totalPrice','ref_code','start_date','ordered_date','billing_address','payment','seller_msg')
    
class SubcriptionAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    # Inject chart data on page load in the ChangeList view
    
class ProfileAdmin(admin.ModelAdmin):
    # list_filter = ("user.groups", )
    list_display = [
        'unique_id',
        'user'
    ]
    readonly_fields = ('unique_id','user')
    def changelist_view(self, request, extra_context=None):
        chart_data = self.chart_data()
        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        extra_context = extra_context or {"chart_data": as_json}
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        extra_urls = [
            path("chart_data/", self.admin_site.admin_view(self.chart_data_endpoint))
        ]
        # NOTE! Our custom urls have to go before the default urls, because they
        # default ones match anything.
        return extra_urls + urls

    # JSON endpoint for generating chart data that is used for dynamic loading
    # via JS.
    def chart_data_endpoint(self, request):
        chart_data = self.chart_data()
        return JsonResponse(list(chart_data), safe=False)

    def chart_data(self):
        return (
            Profile.objects.annotate(date=TruncDay("subs_date"))
            .values("date")
            .annotate(y=Count("id"))
            .order_by("-date")
        )

    



admin.site.register(Item, ItemAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment,CommentAdmin)
#admin.site.register(Attachment)
#admin.site.register(Contact)
#admin.site.register(Slide)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Payment, PaymentAdmin)
#admin.site.register(Coupon) 
admin.site.register(BillingAddress, AddressAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Testimonial)
#admin.site.register(Subcription, SubcriptionAdmin)
#admin.site.register(Seo)
#admin.site.register(HomeImage)



