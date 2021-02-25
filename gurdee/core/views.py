from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm, UserLogInForm, ServiceLogInForm, CreateProductForm, RadioCheckoutForm
from .models import Profile, SubscriptionPayment, Category, Item, Attachment, OrderItem, Attachment, BillingAddress, Payment, Comment, CommentForm, Testimonial, Subcription, Seo, HomeImage
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from django.db.models.functions import ExtractWeek, ExtractMonth, TruncDay
import random
import string
import re
import calendar

from instamojo_wrapper import Instamojo
API_KEY = "test_40664180402e64719e4ad001486"
AUTH_TOKEN = "test_4362430ec6fac7573e1048788af"
api = Instamojo(api_key=API_KEY,auth_token=AUTH_TOKEN,endpoint='https://test.instamojo.com/api/1.1/')


import razorpay
client = razorpay.Client(auth=("rzp_test_gZUdaE6doY9IkN", "x0GVGy02QtV4aqxzAfRuYy2P"))
#client = razorpay.Client(auth=("rzp_test_0EmBEJ2rejSH8g", "yE0M3thBYEZuyRjvm959d1KG"))
# client = razorpay.Client(auth=("rzp_test_bjxg6t7DTXax3c", "kqUVmjRxlXpVcrhKG9dxEnMr"))

'''
    subsdate = 11.11.2020
    boodate = 11.11.2020


'''


def is_SubcriptionOver(user):
    profile = Profile.objects.filter(user=user)
    if profile.exists():
        profile = profile[0]
        if has_Subcription(user):
            if profile.booster:
                delta1 = timezone.now() - profile.subs_date
                delta2 = timezone.now() - profile.booster_date
                print(delta1, delta2)
                # delta = delta1.days - (delta1.days - profile.subcription.validity)
                # delta = delta + delta2.days
                delta = delta1.days + delta2.days
                print(delta)
            elif profile.subcription:
                delta = timezone.now() - profile.subs_date
                delta = delta.days
            else:
                delta = 0

            days = profile.days_valid - delta
            print(profile.days_valid)
            if days <= 0:
                days = 0
            if days > 0:
                #print("0")
                pass
            else:
                #print("1")
                profile.subcription = None
                profile.booster = None
                # profile.days_valid = 0
                profile.entries_remaining = 0
                # profile.subs_date = None
                # profile.booster_date = None
                profile.save()
            return days
        else:
            return 0
    else:
        return False

def has_Subcription(user):
    profile = Profile.objects.filter(user=user)
    if profile.exists():
        profile = profile[0]
        #print(profile.subcription)
        if profile.subcription:
            return True
        else:
            return False   


def is_MaxEntries(user):
    profile = Profile.objects.filter(user=user)
    if profile.exists():
        profile = profile[0]
        #print(profile.entries_remaining)
        if profile.entries_remaining > 0:
            return True
        else:
            return False
    else:
        return False

def has_filledForms(user):
    profile = Profile.objects.filter(user=user)
    if profile.exists():
        profile = profile[0]
        if profile.saved == True and profile.bank_details_saved == True:
            return True
        else:
            return False
    else:
        return False       



def is_customer(user):
    return user.groups.filter(name='Customers').exists()

def is_serviceProvider(user):
    return user.groups.filter(name='Service Providers').exists()

def filter_subs(order, user):
    order = OrderItem.objects.filter(id=order.id)
    profile = Profile.objects.filter(user=user)
    if profile.exists():
        profile = profile[0]
        if order.exists():
            order = order[0]
            mydate = profile.subs_date + timedelta(days=profile.days_valid)
            if order.ordered_date >= mydate:
                return False
            else:
                return True


def welcome_page(request):
    category = Category.objects.filter(is_active=True)
    seos = Seo.objects.all()
    homeImage = HomeImage.objects.filter(is_active=True)
    context = {
        'category' : category,
        'seos' : seos,
        'homeImage' : homeImage
    }
    if request.user.is_authenticated:
        orders = OrderItem.objects.filter(user=request.user,ordered=False)
        if orders.exists():
            context['no_orders'] = len(orders)
        else:
            context['no_orders'] = 0
    #print(context)
    return render(request, 'index.html', context)



@login_required(login_url='/service-provider-login')
def addproduct_page(request):
    if has_filledForms(request.user):
        pass
    else:
        messages.error(request, "Please Fill the Profile and Bank Details")
        return redirect("shop:profile")
    if has_Subcription(request.user):
        pass
    else:
        messages.error(request, "You donot have a Subscription to Post Your Products/Services for Sale. Subscribe to continue")
        return redirect("shop:subscription")
    if is_SubcriptionOver(request.user) and is_MaxEntries(request.user):
    

        if request.method == 'POST':
            #print(request.POST)
            title=request.POST['service_name']
            price=request.POST['price']
            brandName = request.POST['brand_name']
            discount_price=request.POST['Discount_price']
            if discount_price == '':
                discount_price = False
            category_id=request.POST['category']
            if category_id != 0 or category_id != "0":
                category = Category.objects.filter(id=category_id)
                if category.exists():
                    category = category[0]

            label = "New"
            slug = title.lower()
            stock_no=request.POST['stock_number']
            description_short=request.POST['Product_Description']
            description_long=request.POST['Shipping_Details']
            image=request.FILES['upload_image']
            my_dict = dict(request.POST)
            state = request.POST['state']
            city = request.POST['city']
            profile = Profile.objects.filter(user=request.user)
            if profile.exists():
                profile=profile[0]
            item = Item.objects.create(
                seller=profile,
                title=title, price=price, 
                discount_price=discount_price,
                category=category,
                label=label,
                slug=slug,
                stock_no=stock_no,
                description_short=description_short,
                description_long=description_long,
                image=image,
                is_active=True,
                has_variations=False,
                state=state,
                city=city, 
                brandName=brandName
                )
            id = item.id
            item.unique_id = "S"+str(profile.id)+"P"+str(id)
            item.save()
            profile.entries_remaining -= 1
            profile.save()
            #print(request.FILES)
            try:
                for f in request.FILES.getlist('files[]'):
                    attachment = Attachment.objects.create(productId=item, media_attach=f)
            except:
                pass
            return redirect("shop:serviceproduct")
        category = Category.objects.filter(is_active=True)
        form = CreateProductForm()
        profile=Profile.objects.filter(user=request.user)
        if profile.exists():
            profile=profile[0]
        context = {
            'category':category,
            'form' : form,
            'profile':profile
        }
        return render(request, 'addproduct.html', context)
    else:
        if is_SubcriptionOver(request.user):
            pass
        else:
            messages.error(request, "You donot have a Subscription to Post Your Products/Services for Sale. Subscribe to continue")
        if is_MaxEntries(request.user):
            pass
        else:
            messages.error(request, "You have Exhausted the Limit of Your Maximum Entries.  Buy a Add-On to Continue")
        return redirect("shop:subscription")


@login_required
def cart_page(request):
    cart = OrderItem.objects.filter(user=request.user,ordered=False)
    category = Category.objects.filter(is_active=True)
    context = {}
    context['object'] = cart
    context['category'] = category
    if cart.exists():
        context['no_orders'] = len(cart)
    else:
        context['no_orders'] = 0
    sub_total = 0
    grand_total = 0
    tax_amount = 0
    for item in cart:
        sub_total = sub_total + item.price
        grand_total = grand_total + item.totalPrice
        tax_amount = tax_amount + item.tax
    context['tax_amount'] = tax_amount
    context['sub_total'] = sub_total
    context['grand_total'] = grand_total
    return render(request, 'cart.html', context)


@login_required
def changepassword_page(request):
    return render(request, 'changepassword.html')


@login_required
def confirpasswordmessage_page(request):
    return render(request, 'confirmpasswordmessage.html')


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

@login_required
def checkout_page(request):
    if request.method == "POST":
        #print(request.POST)
        fname = request.POST['q2_fullName2[first]']
        lname = request.POST["q2_fullName2[last]"]
        email = request.POST['q3_email3']
        phoneNo = request.POST['q5_contactNumber[full]']
        address1 = request.POST['q4_billingAddress[addr_line1]']
        address2 = request.POST['q4_billingAddress[addr_line2]']
        city = request.POST['q4_billingAddress[city]']
        state = request.POST['q4_billingAddress[state]']
        zip = request.POST['q4_billingAddress[postal]']
        payment_option = request.POST['payment_option']
        
        order = OrderItem.objects.filter(user=request.user, ordered=False)
        if order.exists():
            billing_address = BillingAddress(
                user=request.user,
                fname=fname,
                lname=lname,
                email=email,
                street_address=address1,
                apartment_address=address2,
                city=city,
                state=state,
                zip=zip,
                address_type='B',
                number=phoneNo
            )
            billing_address.save()
            try:
                billing_address.specialInstructions = request.POST['q14_specialInstructions']
                billing_address.save()
            except:
                pass
            
            totalPrice = 0
            for i in order:
                totalPrice += i.totalPrice
                i.billing_address = billing_address
                i.save()

            amount = float(totalPrice)
            purpose = "order"
            user = User.objects.get(username=request.user)
            name = str(order[0])

            if payment_option == "InstaMojo":
                response = api.payment_request_create(
                            amount=amount,
                            purpose=purpose,
                            buyer_name=user,
                            redirect_url="http://localhost:8000/myorders"
                            )
            

                if(response['success']):                    
                    messages.success(request, "Order was successful")
                    return redirect(response['payment_request']['longurl'])
            elif payment_option == "RazorPay":
                razorpayResponse = client.order.create(dict(
                                    amount=amount*100,
                                    currency="INR",
                                    receipt=create_ref_code(),
                                    ))
                order_id = razorpayResponse['id']
                order_status = razorpayResponse['status']

                if order_status=='created':

                    order = OrderItem.objects.filter(user=request.user, ordered=False)
                    categorys = Category.objects.filter(is_active=True)
                    context = {
                        'order': order,
                        'DISPLAY_COUPON_FORM': True,
                        'category' : categorys,
                    }
                    context['order_id'] = order_id
                    context['price'] = amount
                    context['name'] = fname
                    context['phone'] = phoneNo
                    context['email'] = email
                    sub_total = 0
                    grand_total = 0
                    tax_amount = 0
                    for item in order:
                        sub_total = sub_total + item.price
                        grand_total = grand_total + item.totalPrice
                        tax_amount = tax_amount + item.tax
                    context['tax_amount'] = tax_amount
                    context['sub_total'] = sub_total
                    context['grand_total'] = grand_total
                    return render(request, "checkout.html", context)
                return redirect("shop:checkout")
            elif payment_option == "COD":
                order = OrderItem.objects.filter(user=request.user, ordered=False)
                myTime = timezone.now()
                for item in order:
                    payment = Payment()
                    payment.stripe_charge_id = "COD"
                    payment.user = request.user
                    payment.amount = item.totalPrice
                    payment.save()
                    item.ordered = True
                    item.ordered_date = myTime
                    item.payment = payment
                    item.ref_code = create_ref_code()
                    item.save()
                return redirect("shop:myorders")

    order = OrderItem.objects.filter(user=request.user, ordered=False)
    form = RadioCheckoutForm()
    context = {
        'form'  : form
    }
    if order.exists():
        context['order'] = order
        sub_total = 0
        grand_total = 0
        tax_amount = 0
        for item in order:
            sub_total = sub_total + item.price
            grand_total = grand_total + item.totalPrice
            tax_amount = tax_amount + item.tax
        context['tax_amount'] = tax_amount
        context['sub_total'] = sub_total
        context['grand_total'] = grand_total
    return render(request, 'checkout.html', context)


def payment_status(request):
    if request.method == "POST":
        #print("in post")
        #print(request.POST)
        params_dict = {
            'razorpay_payment_id' : request.POST.get('razorpay_payment_id'),
            'razorpay_order_id' : request.POST.get('razorpay_order_id'),
            'razorpay_signature' : request.POST.get('razorpay_signature')
        }

        #print(params_dict)
        # VERIFYING SIGNATURE
        try:
            #print("in tyr")
            response = client.order.fetch(params_dict['razorpay_order_id'])
            # status = client.utility.verify_payment_signature(params_dict)
            #print("status", response)
            if response['status'] == "paid" and response['amount_due'] == 0:
                order = OrderItem.objects.filter(user=request.user, ordered=False)
                myTime = timezone.now()
                for item in order:
                    payment = Payment()
                    payment.stripe_charge_id = response['id']
                    payment.user = request.user
                    payment.amount = item.totalPrice
                    payment.save()
                    item.ordered = True
                    item.payment = payment
                    item.ordered_date = myTime
                    item.ref_code = response['receipt']
                    item.save()
            messages.success(request, "Your Order Has been Placed Successfully")         
            return redirect("shop:myorders")
        except:
            return redirect("shop:checkout")
    else:
        print("out of  post")


def boosterdays(profile):
    if profile.booster:
        return profile.booster.validity
        delta2 = timezone.now() - profile.booster_date
        delta = profile.booster.validity - delta2.days
        print(delta2.days, delta)
        return delta
    return 0


def subcription_payment_status(request, id):
    if request.method == "POST":
        #print("in post")
        #print(request.POST)
        params_dict = {
            'razorpay_payment_id' : request.POST.get('razorpay_payment_id'),
            'razorpay_order_id' : request.POST.get('razorpay_order_id'),
            'razorpay_signature' : request.POST.get('razorpay_signature')
        }

        #print(params_dict)
        # VERIFYING SIGNATURE
        # response = client.order.fetch(params_dict['razorpay_order_id'])
        # print(responce)
        try:
            #print("in tyr")
            response = client.order.fetch(params_dict['razorpay_order_id'])
            # print(response)
            # status = client.utility.verify_payment_signature(params_dict)
            #print("status", response)
            obj = SubscriptionPayment.objects.create(
                user=request.user,
                price=response["amount"] / 100
            )
            obj.save()
            print(response)
            if response['status'] == "paid" and response['amount_due'] == 0:
                profile = Profile.objects.filter(user=request.user)
                subscription = Subcription.objects.filter(id=id)
                if profile.exists() and subscription.exists():
                    profile = profile[0]
                    subscription = subscription[0]
                    if subscription.is_booster:
                        profile.booster = subscription
                        profile.entries_remaining += subscription.entries
                        profile.days_valid += subscription.validity
                        profile.booster_date = timezone.now()
                        profile.save()
                    else:
                        profile.subcription = subscription
                        profile.entries_remaining = subscription.entries
                        profile.days_valid = subscription.validity + boosterdays(profile)
                        profile.subs_date = timezone.now()
                        # profile.booster_date = None
                        profile.save()
                messages.success(request, "Your Subscription Plan is Activated Successfully")        
                return redirect("shop:profile")
                
            else:
                raise ValueError
        except Exception as e:
            print(str(e))
            return redirect("shop:subscription")
    else:
        print("out of  post")

def customerregistrtion_page(request):
    return render(request, 'customerregistrtion.html')


@login_required
def forgotpassword_page(request):
    return render(request, 'forgotpassword.html')

@login_required
def forgotpasswordmessage_page(request):
    return render(request, 'forgotpasswordmessage.html')


@login_required(login_url='shop:index')
def user_logout_page(request):
    logout(request)
    return redirect('shop:index')


def customer_login_page(request):
    if request.user.is_authenticated:
        return redirect('shop:index')
    else:
        form = UserLogInForm()
        if request.method == 'POST':
            form = UserLogInForm(request.POST)
            if form.is_valid:
                username = form.data.get("username")
                password = form.data.get("password")
                #print(username, password)
                user = authenticate(username=username, password=password)
                if user:
                    if is_customer(user):
                        login(request, user)
                        messages.success(request, "Logined In as a Customer")
                        return redirect('shop:index')
                messages.error(request, "User Id And Password doesn't match.")
                return redirect("shop:login")
        category = Category.objects.filter(is_active=True)
        context = {'form': form,'category':category}
        return render(request, 'customer_login.html', context)


def service_login_page(request):
    if request.user.is_authenticated:
        return redirect('shop:ordersreceived')
    else:
        form = ServiceLogInForm()
        if request.method == 'POST':
            form = ServiceLogInForm(request.POST)
            if form.is_valid:
                username = form.data.get("username")
                password = form.data.get("password")
                #print(username, password)
                user = authenticate(username=username, password=password)
                if user:
                    if is_serviceProvider(user):
                        login(request, user)
                        messages.success(request, "Logined In as a Service Provider")
                        return redirect('shop:profile')
                messages.error(request, "User Id And Password doesn't match.")
                return redirect("shop:service_login_page")
        context = {'form': form}
        return render(request, 'servicepro_login.html', context)


@login_required
def myorders_page(request):
    try:
        if request.GET.get('payment_id') and request.GET.get('payment_request_id'):
           
            payment_id = request.GET.get('payment_id') 
            payment_request_id =  request.GET.get('payment_request_id')
            secondResponse = api.payment_request_payment_status(payment_request_id, payment_id)
            
            #print(secondResponse)
            if secondResponse['payment_request']['status'] == 'Completed' and secondResponse['payment_request']['payment']['failure'] == None and secondResponse['payment_request']['payment']['status'] == 'Credit':
               
                order = OrderItem.objects.filter(user=request.user, ordered=False)
                myTime = timezone.now()
                for item in order:
                    payment = Payment()
                    payment.stripe_charge_id = secondResponse['payment_request']['id']
                    payment.user = request.user
                    payment.amount = item.totalPrice
                    payment.save()
                    item.ordered = True
                    item.payment = payment
                    item.ordered_date = myTime
                    item.ref_code = create_ref_code()
                    item.save()
    except:
        pass
    orders = OrderItem.objects.filter(user=request.user, ordered=True).order_by("-id")   
    category = Category.objects.filter(is_active=True)
    profile = Profile.objects.filter(user=request.user)
    context = {
        'orders' : orders,
        'category' : category
    }
    if profile.exists():
        context['profile'] = profile[0]
    orders = OrderItem.objects.filter(user=request.user,ordered=False)
    if orders.exists():
        context['no_orders'] = len(orders)
    else:
        context['no_orders'] = 0
    return render(request, 'myorders.html', context)

@login_required(login_url='/service-provider-login')
def ordersreceived_page(request):
    if has_filledForms(request.user):
        pass
    else:
        messages.error(request, "Please Fill the Profile and Bank Details")
        return redirect("shop:profile")
    if is_serviceProvider(request.user):
        profile = Profile.objects.filter(user=request.user)
        context = {}
        if profile.exists():
            profile = profile[0]
            orders = OrderItem.objects.filter(item__seller=profile, ordered=True).order_by('-id')
            orders_list = []
            context['profile'] = profile
            context['no_orders'] = len(orders)
            with_in_sub = []
            for i in orders:
                #print("----", i.id)
                if filter_subs(i, request.user):
                    with_in_sub.append(i)
                orders_list.append(i)
            totalOrders=ordersPending=ordersAccepted=ordersCancelled=ordersDelivered=0
            for order in orders:
                totalOrders+=1
                if order.order_placed==False and order.order_rejected==False:
                    ordersPending+=1
                if order.order_placed==True and order.being_delivered==False:
                    ordersAccepted+=1
                if order.order_rejected==True:
                    ordersCancelled+=1
                if order.order_placed==True and order.being_delivered==True:
                    ordersDelivered+=1
            context['ordersPending'] = ordersPending
            context['ordersAccepted'] = ordersAccepted
            context['ordersCancelled'] = ordersCancelled
            context['ordersDelivered'] = ordersDelivered
            context['totalOrders'] = totalOrders
            paginator = Paginator(orders_list, 10)
            page_number = request.GET.get('page')
            if not page_number:
                page_number=1
            page_obj = paginator.get_page(page_number)
            #print("in page" , page_obj)
            context['orders'] = page_obj
            context['subsDate'] = is_SubcriptionOver(request.user)
            #print(is_SubcriptionOver(request.user))
            if is_SubcriptionOver(request.user) > 0:
                context['displayInfo'] = True
            else:
                context['displayInfo'] = False
                paginator = Paginator(with_in_sub, 10)
                page_number = request.GET.get('page')
                if not page_number:
                    page_number=1
                page_obj = paginator.get_page(page_number)
                context['orders'] = page_obj
        return render(request, 'ordersreceived.html', context)
    return redirect("shop:index")

@login_required

@login_required(login_url='/login')
def product_page(request, slug, id):
    category = Category.objects.filter(is_active=True)
    my_category =  Category.objects.filter(id=id)
    context = {
        'id' : id,
        'category' : category
    }
    if my_category.exists():
        my_category = my_category[0]
        context['my_category'] = my_category
    orders = OrderItem.objects.filter(user=request.user,ordered=False)
    if orders.exists():
        context['no_orders'] = len(orders)
    else:
        context['no_orders'] = 0
    id_category = Category.objects.filter(id=id)
    item_list = []
    if id_category.exists():
        id_category = id_category[0]
        items = Item.objects.filter(category=id_category, is_active=True)
        paginator = Paginator(items, 45)
        page_number = request.GET.get('page')
        if not page_number:
            page_number=1
        page_obj = paginator.get_page(page_number)
        context['orders'] = page_obj
        context['currentPage'] = page_number
        #print(page_obj)
    return render(request, 'product.html', context)


def product_page_json(request, id):
    category = Category.objects.filter(id=id)
    item_list = []
    if category.exists():
        category = category[0]
        items = Item.objects.filter(category=category, is_active=True)
        paginator = Paginator(items, 45)
        page_number = request.GET.get('page')
        if not page_number:
            page_number=1
        page_obj = paginator.get_page(page_number)
        for item in page_obj:
            temp_dict = {}
            temp_dict['id'] = item.id
            temp_dict['slug'] = item.slug
            temp_dict['make'] = item.city
            temp_dict['model'] = item.title
            if item.discount_price:
                temp_dict['price'] = str(item.discount_price)
            else:
                temp_dict['price'] = str(item.price)
            temp_dict['image'] = item.image.url
            temp_dict['type'] = item.state
            try:
                if item.seller.booster.has_priority_support or item.seller.subcription.has_priority_support:
                    temp_dict['priority'] = True
                else:
                    temp_dict['priority'] = False
            except:
                temp_dict['priority'] = False
            item_list.append(temp_dict)
    #print(item_list)
    return JsonResponse(item_list, safe=False)

@login_required(login_url='/login')
def productpage_page(request, slug, id):
    item = Item.objects.filter(id=id)
    category = Category.objects.filter(is_active=True)
    context = {
        'category' : category
    }
    orders = OrderItem.objects.filter(user=request.user,ordered=False)
    if orders.exists():
        context['no_orders'] = len(orders)
    else:
        context['no_orders'] = 0
    if item.exists():
        item = item[0]
        attachments = Attachment.objects.filter(productId=item)
        context['item'] = item
        comment = Comment.objects.filter(product=item, status='True')
        #print(comment)
        form = CommentForm()
        context['form'] = form
        if attachments.exists():
            context['attachment'] = attachments
        if comment.exists():
            context['comment'] = comment
    return render(request, 'product-page.html', context)


@login_required(login_url='/service-provider-login')
def profile_page(request):
    if request.method == 'POST':
        company_name = request.POST['cname']
        address1 = request.POST['Address1']
        address2 = request.POST['Address2']
        state = request.POST['state']
        city = request.POST['city']
        zip = request.POST['zip']
        profile = Profile.objects.filter(user=request.user)
        if profile.exists():
            profile = profile[0]
            profile.company_name = company_name
            profile.address1 = address1
            profile.address2 = address2
            profile.state = state
            profile.city = city
            profile.zip = zip
            profile.saved = True
            profile.save()
    user_obj = User.objects.get(username=request.user)
    user = user_obj
    profile = Profile.objects.filter(user=user)
    orders = []
    if profile.exists():
        profile = profile[0]
        orders = OrderItem.objects.filter(item__seller=profile, ordered=True)
    
    context = {'user': user,'profile':profile,"no_orders": len(orders)}
    #print(user.username)
    return render(request, 'profile.html', context)

def addbankdetails(request):
    if request.method == "POST":
        account_number = request.POST['account_number']
        ifsc_code = request.POST['ifsc']
        account_holder_name = request.POST['account_name']
        bank_name = request.POST['bank_name']
        profile = Profile.objects.filter(user=request.user)
        if profile.exists():
            profile = profile[0]
            profile.account_number = account_number
            profile.account_holder_name = account_holder_name
            profile.ifsc_code = ifsc_code
            profile.bank_name = bank_name
            profile.bank_details_saved = True
            profile.save()
        return redirect("shop:profile")

def registration_page(request, backend='django.contrib.auth.backends.ModelBackend'):
    if request.user.is_authenticated:
        return redirect('shop:index')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            fname = request.POST['first_name']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            phoneNo = request.POST['contact_number']
            email = request.POST['username']
            rex = '^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])\w{6,}$'
            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email ID already taken.    Do Login If You Are An Existing User ")
                return  redirect('shop:registration')
            elif re.search(regex,email) == None:
                messages.error(request, "Enter proper email ID")
                return  redirect('shop:registration')

            elif phoneNo == "" or phoneNo == " " or len(phoneNo) < 9:
                messages.error(request, "Please Enter Proper Contact Number.")
                return redirect('shop:registration')
                
 
            elif re.search(rex,password1) == None:
                messages.error(request, " Password must be a combination at least six characters at least one number, one lowercase and one uppercase letter")
                return  redirect('shop:registration')


            elif password1 != password2:
                messages.error(request, "Entered Passwords are not same")
                return redirect('shop:registration')
            else:
                user = User.objects.create_user(username=email, email=email,  password=password1)
                user.first_name = fname
                user.groups.add(1)# 2 - Service Providers
                user.save()
                profile_obj = Profile.objects.create(
                    user=user,
                    contact_number=request.POST['contact_number'],
                    is_service_provider=False
                )
                try:
                    profile_obj.alt_contact_number=request.POST['alt_contact_number']
                except:
                    pass
                id = profile_obj.id
                profile_obj.unique_id = 'C'+str(id)
                profile_obj.save()
                messages.success(request,"User is Registered Successfully")
                return redirect('shop:login')
        context = {'form': form}
        return render(request, 'register.html', context)



def registration_sp_page(request):
    if request.user.is_authenticated:
        return redirect('shop:ordersreceived')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            fname = request.POST['first_name']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            phoneNo = request.POST['contact_number']
            email = request.POST['username']
            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email ID already taken.    Do Login If You Are An Existing User ")
                return  redirect('shop:registration_sp')
            elif re.search(regex,email) == None:
                messages.error(request, "Enter proper email ID")
                return  redirect('shop:registration_sp')
            elif phoneNo == "" or phoneNo == " " or len(phoneNo) < 1:
                messages.error(request, "Please Enter Proper Contact Number.")
                return redirect('shop:registration_sp')
            elif password1 != password2:
                messages.error(request, "Entered Passwords are not same")
                return redirect('shop:registration_sp')
            else:
                user = User.objects.create_user(username=email, email=email,  password=password1)
                user.first_name = fname
                user.groups.add(2)# 2 - Service Providers
                user.save()
                profile_obj = Profile.objects.create(
                    user=user,
                    contact_number=phoneNo,
                    is_service_provider=True,
                )
                try:
                    profile_obj.alt_contact_number=request.POST['alt_contact_number']
                except:
                    pass
                id = profile_obj.id
                profile_obj.unique_id = 'S'+str(id)
                profile_obj.save()
                messages.success(request,"User is Registered Successfully")
                return redirect('shop:service_login_page')
        context = {'form': form}
        return render(request, 'register_sp.html', context)

@login_required(login_url='/service-provider-login')
def serviceproduct_page(request):
    if has_filledForms(request.user):
        pass
    else:
        messages.error(request, "Please Fill the Profile and Bank Details")
        return redirect("shop:profile")

    # if is_SubcriptionOver(request.user):
    #     pass
    # else:
    #     return redirect("shop:subscription")
    profile = Profile.objects.filter(user=request.user)
    context = {}
    if profile.exists():
        profile = profile[0]
        orders = OrderItem.objects.filter(item__seller=profile, ordered=True)
        items = Item.objects.filter(seller=profile, is_active=True)
        context['items'] = items
        context['no_orders'] = len(orders)
    return render(request, 'serviceproduct.html', context)

@login_required(login_url='/service-provider-login')
def servicesingleproduct_page(request, slug, id):
    if has_filledForms(request.user):
        pass
    else:
        messages.error(request, "Please Fill the Profile and Bank Details")
        return redirect("shop:profile")
    # if is_SubcriptionOver(request.user):
    #     pass
    # else:
    #     return redirect("shop:subscription")
    item = Item.objects.filter(id=id)
    context = {}
    if item.exists():
        item = item[0]
        attachments = Attachment.objects.filter(productId=item)
        comment = Comment.objects.filter(product=item, status='True')
        if comment.exists():
            context['comment'] = comment
        context['item'] = item
        if attachments.exists():
            context['attachment'] = attachments
    return render(request, 'servicesingleproduct.html', context)

@login_required(login_url='/service-provider-login')
def subscription_page(request):
    if has_filledForms(request.user):
        pass
    else:
        messages.error(request, "Please Fill the Profile and Bank Details")
        return redirect("shop:profile")
    if is_SubcriptionOver(request.user):
        pass
    else:
        pass
    subscriptions = Subcription.objects.all()
    has_booster = 0
    for i in subscriptions:
        if i.is_booster == True:
            has_booster = 1
            break
    context = {
        'subscriptions' : subscriptions,
        'has_booster' : has_booster,
        'buying' : False
    }
    profile = Profile.objects.filter(user=request.user)
    if profile.exists():
        profile = profile[0]
        orders = OrderItem.objects.filter(item__seller=profile, ordered=True)
        context['no_orders'] = len(orders)
        if profile.subcription:
            context['mySubs'] = profile.subcription
            if profile.booster:
                context['myBoost'] = profile.booster
            
    return render(request, 'subscription.html', context)

def tempView(request, id):
    try:
        if request.GET.get('payment_id') and request.GET.get('payment_request_id'):
           
            payment_id = request.GET.get('payment_id') 
            payment_request_id =  request.GET.get('payment_request_id')
            secondResponse = api.payment_request_payment_status(payment_request_id, payment_id)
            
            #print(secondResponse)
            if secondResponse['payment_request']['status'] == 'Completed' and secondResponse['payment_request']['payment']['failure'] == None and secondResponse['payment_request']['payment']['status'] == 'Credit':
                profile = Profile.objects.filter(user=request.user)
                subscription = Subcription.objects.filter(id=id)
                if profile.exists() and subscription.exists():
                    profile = profile[0]
                    subscription = subscription[0]
                    if subscription.is_booster:
                        profile.booster = subscription
                        profile.entries_remaining += subscription.entries
                        profile.days_valid += subscription.validity
                        profile.booster_date = timezone.now()
                        profile.save()
                    else:
                        profile.subcription = subscription
                        profile.entries_remaining = subscription.entries
                        profile.days_valid = subscription.validity
                        profile.subs_date = timezone.now()
                        profile.booster_date = None
                        profile.save()
                return redirect("shop:profile")
            else:
                return redirect("shop:subscription")
    except:
        return redirect("shop:subscription")


def buySubcription(request, id):
    if request.method == "POST":
        payment_option = request.POST['payment_option']
        subscription = Subcription.objects.filter(id=id)
        profile = Profile.objects.filter(user=request.user)
        if subscription.exists() and profile.exists():
            subscription = subscription[0]
            profile = profile[0]
            if subscription.is_booster:
                if profile.subcription :
                    pass
                else:
                    return redirect("shop:subscription")
        else:
            return redirect("shop:profile")

        if payment_option == 'InstaMojo':
            response = api.payment_request_create(
                            amount=subscription.price,
                            purpose="Buying" + str(subscription.name)+" Subcription",
                            buyer_name=profile,
                            redirect_url="http://localhost:8000/tempView/"+str(subscription.id)+"/"
                            )

            if(response['success']):                    
                messages.success(request, "Order was successful")
                return redirect(response['payment_request']['longurl'])
        elif payment_option == 'RazorPay':
            razorpayResponse = client.order.create(dict(
                                    amount=subscription.price*100,
                                    currency="INR",
                                    receipt=create_ref_code(),
                                    ))
            order_id = razorpayResponse['id']
            order_status = razorpayResponse['status']

            if order_status=='created':
                context = {
                    'subs': subscription,
                    'DISPLAY_COUPON_FORM': True,
                    'buying' : True
                }
                context['order_id'] = order_id
                context['price'] = subscription.price
                context['name'] = profile.user.username
                context['phone'] = profile.contact_number
                context['email'] = profile.user.username
                return render(request, "subscription.html", context)
            return redirect("shop:subscription")

    subscription = Subcription.objects.filter(id=id)
    profile = Profile.objects.filter(user=request.user)
    if subscription.exists() and profile.exists():
        subscription = subscription[0]
        profile = profile[0]
        if subscription.is_booster:
            if profile.subcription :
                pass
            else:
                return redirect("shop:subscription")
        # context = {
        #     'subs' : subscription,
        #     'buying' : True
        # }
        # return render(request, 'subscription.html', context)

        razorpayResponse = client.order.create(dict(
                                    amount=subscription.price*100,
                                    currency="INR",
                                    receipt=create_ref_code(),
                                    ))
        order_id = razorpayResponse['id']
        order_status = razorpayResponse['status']

        if order_status=='created':
            context = {
                'subs': subscription,
                'DISPLAY_COUPON_FORM': True,
                'buying' : True
            }
            context['order_id'] = order_id
            context['price'] = subscription.price
            context['name'] = profile.user.username
            context['phone'] = profile.contact_number
            context['email'] = profile.user.username
            return render(request, "subscription.html", context)
        return redirect("shop:subscription")

    else:
        return redirect("shop:subscription")


def testimonials_page(request):
    if request.method == 'POST':
        name = request.POST['email']
        try:
            role = request.POST['role']
        except:
            role = 'Seller' 
        testimonial = request.POST['testimonial']
        new_testimonial = Testimonial(
                                name=name,
                                role=role,
                                testimonial=testimonial
                            )
        new_testimonial.save()
        messages.success(request, 'Thank You for Contacting us we will soon get back to you.')
        return redirect("shop:testimonials")
    testimonials = Testimonial.objects.filter(display=True)
    context = {
        'testimonials' : testimonials
    }
    return render(request, 'testimonials.html', context)

@login_required(login_url='/service-provider-login')
def updateproduct_page(request, slug, id):
    if has_filledForms(request.user):
        pass
    else:
        messages.error(request, "Please Fill the Profile and Bank Details")
        return redirect("shop:profile")
    if request.method == 'POST':
        #print(request.POST)
        title=request.POST['service_name']
        price=request.POST['price']
        discount_price=request.POST['Discount_price']
        if discount_price == '':
            discount_price = False
        #print("Discount_price", discount_price)
        category_id=request.POST['category']
        if category_id != 0 or category_id != "0":
            category = Category.objects.filter(id=category_id)
            if category.exists():
                category = category[0]

        label = "New"
        slug = title.lower()
        brandName = request.POST['brand_name']
        stock_no=request.POST['stock_number']
        description_short=request.POST['Product_Description']
        description_long=request.POST['Shipping_Details']
        state = request.POST['state']
        city = request.POST['city']
        profile = Profile.objects.filter(user=request.user)
        if profile.exists():
            profile=profile[0]
        item = Item.objects.get(id=id)
        item.title = title
        item.price=price
        item.discount_price = discount_price
        item.category = category
        item.slug = slug
        item.stock_no = stock_no
        item.state = state
        item.city = city
        item.brandName = brandName
        item.description_short = description_short
        item.description_long = description_long
        try:
            image=request.FILES['upload_image']
            item.image = image
        except:
            pass
        item.save()

        try:
            for f in request.FILES.getlist('files[]'):
                attachment = Attachment.objects.create(productId=item, media_attach=f)
        except:
            pass
        return redirect("shop:serviceproduct")

    category = Category.objects.filter(is_active=True)
    item = Item.objects.filter(id=id)
    if item.exists():
        item = item[0]
        attachments = Attachment.objects.filter(productId=item)
    form = CreateProductForm()
    context = {
        'category':category,
        'form' : form,
        'item' : item,
        'attachments':attachments
    }
    return render(request, 'updateproduct.html', context)


# carts

def addItemToCart(request, id, qt):
    item = Item.objects.get(id=id)
    if item.discount_price:
        price = item.discount_price
    else:
        price = item.price
    cart_items = OrderItem.objects.filter(item=item, ordered=False)
    if cart_items.exists():
        cart_item = cart_items[0]
        cart_item.quantity += int(qt)
        cart_item.price = cart_item.price + (int(qt) * price)
        cart_item.save()
        if cart_item.totalPrice == None:
            cart_item.totalPrice = 0
        cart_item.totalPrice = cart_item.totalPrice + (int(qt) * price)
        cart_item.save()
        #print("tax...", cart_item.getTaxAmount())
        cart_item.tax = cart_item.getTaxAmount()
        cart_item.save()
        cart_item.totalPrice = cart_item.price + cart_item.tax
        cart_item.save()
        #print(cart_item.price, cart_item.totalPrice, cart_item.tax)
    else:
        new_cartItem = OrderItem.objects.create(
            user=request.user,item=item, quantity=int(qt),price=int(qt) * price)
        if new_cartItem.totalPrice == None:
            new_cartItem.totalPrice = 0
        new_cartItem.totalPrice = new_cartItem.totalPrice + new_cartItem.price
        new_cartItem.save()
        #print("tax...", new_cartItem.getTaxAmount())
        new_cartItem.tax = new_cartItem.getTaxAmount()
        new_cartItem.save()
        new_cartItem.totalPrice  = new_cartItem.price + new_cartItem.tax
        new_cartItem.save()
        new_cartItem.unique_id = 'O'+str(new_cartItem.id)
        new_cartItem.save()
        #print(new_cartItem.price, new_cartItem.totalPrice, new_cartItem.tax)

    return redirect("shop:cart")

def removeFromCart(request, id):
    cart_item = OrderItem.objects.filter(id=id)
    if cart_item.exists():
        cart_item = cart_item[0]
        cart_item.delete()
    return redirect("shop:cart")

def deleteItem(request, id):
    item = Item.objects.filter(id=id)
    profile = Profile.objects.filter(user=request.user)
    if profile.exists():
        profile = profile[0]
    if item.exists():
        item = item[0]
        item.delete()
        profile.entries_remaining += 1
        profile.save()
    return redirect("shop:serviceproduct")

def deleteAttachment(request, id, mainid):
    attachment = Attachment.objects.filter(id=id)
    if attachment.exists():
        attachment = attachment[0]
        attachment.delete()
    category = Category.objects.filter(is_active=True)
    item = Item.objects.filter(id=mainid)
    if item.exists():
        item = item[0]
        attachments = Attachment.objects.filter(productId=item)
    form = CreateProductForm()
    context = {
        'category':category,
        'form' : form,
        'item' : item,
        'attachments':attachments
    }
    return render(request, 'updateproduct.html', context)
    # return redirect("shop:updateproduct")

def addcomment(request,id):
    url = request.META.get('HTTP_REFERER')  # get last url
    if request.method == 'POST':  # check post

        data = Comment()  # create relation with model
        #print (request.POST)
        data.subject = request.POST['name']
        data.email = request.POST['email']
        data.comment = request.POST['comment']
        try:
        	data.rate = request.POST['rating']
        except:
        	data.rate = 1
        data.ip = request.META.get('REMOTE_ADDR')
        profile = Profile.objects.filter(user=request.user)
        if profile.exists():
        	profile = profile[0]
        	pro_id = profile.unique_id
        else:
        	messages.error(request, "Admin cannot place a comment")
        	return HttpResponseRedirect(url)
        item = Item.objects.get(id=id)
        item_id=item.unique_id
        seller_id = item.seller.unique_id

        data.product=Item.objects.get(id=id)
        data.user=User.objects.get(username=request.user)
        data.save()  
        data.unique_id=str(pro_id)+str(item_id)+"Co"+str(data.id)
        data.save()
        messages.success(request, "Your review has ben sent. Thank you for your interest.")
        return HttpResponseRedirect(url)
    return HttpResponseRedirect(url)


def accept_order(request, id):
    if is_serviceProvider(request.user):
        marked = OrderItem.objects.get(id=id)
        marked.order_placed = True
        marked.save()
    return redirect("shop:ordersreceived")


def decline_order(request):
    
    if request.method == "POST":
        try:
            id = request.POST['data']
            msg = request.POST['msg']
        except:
            messages.error(request, "Could not cancel the order. ")
            return redirect("shop:ordersreceived")
        if is_serviceProvider(request.user):
            marked = OrderItem.objects.get(id=id)
            marked.order_rejected = True
            marked.seller_msg = msg
            marked.save()
    return redirect("shop:ordersreceived")


def delivered_order(request, id):
    if is_serviceProvider(request.user):
        marked = OrderItem.objects.get(id=id)
        marked.being_delivered = True
        marked.save()
    return redirect("shop:ordersreceived")

def removeSingleItem(request, id):
    item = Item.objects.get(id=id)
    if item.discount_price:
        price = item.discount_price
    else:
        price = item.price
    cart_items = OrderItem.objects.filter(item=item, ordered=False)
    if cart_items.exists():
        cart_item = cart_items[0]
        if cart_item.quantity == 1:
            cart_item.delete()
            return redirect("shop:cart")
        cart_item.quantity -= 1
        cart_item.price = cart_item.price -  price
        cart_item.save()
        if cart_item.totalPrice == None:
            cart_item.totalPrice = 0
        cart_item.totalPrice = cart_item.totalPrice -  price
        cart_item.save()
        #print("tax...", cart_item.getTaxAmount())
        cart_item.tax = cart_item.getTaxAmount()
        cart_item.save()
        cart_item.totalPrice = cart_item.price + cart_item.tax
        cart_item.save()
        #print(cart_item.price, cart_item.totalPrice, cart_item.tax)
    

    return redirect("shop:cart")

def addMsg(request, id):
    if request.method == "POST":
        orderItems = OrderItem.objects.filter(id=id)
        if orderItems.exists():
            orderItem = orderItems[0]
            if request.POST['msg'] == "":
                # orderItem.seller_msg = False
                pass
            else:
                orderItem.seller_msg = request.POST['msg']
            orderItem.save()
        return redirect("shop:ordersreceived")
    else:
        return redirect("shop:ordersreceived")


@staff_member_required
def payment_graph_view(request):    
    day_items = Payment.objects.annotate(day=TruncDay('timestamp')).values('day').annotate(sum=Sum('amount')).values('day', 'sum')
    day_items = list(day_items)
    dates = [x.get('day').date() for x in day_items]
    new_day_items = []
    if request.method == 'POST':
        datetime_object = datetime.strptime(request.POST['date'], '%m/%d/%Y')
        for d in (datetime_object - timedelta(days=x) for x in range(0,30)):
            if d.date() not in dates:
                new_day_items.append({'day': d, 'sum': 0})
            else:
                for i in day_items:
                    if i["day"].date() == d.date():
                        new_day_items.append({'day': d, 'sum': i["sum"]})
    else:
        for d in (datetime.today() - timedelta(days=x) for x in range(0,30)):
            if d.date() not in dates:
                new_day_items.append({'day': d, 'sum': 0})
            else:
                for i in day_items:
                    if i["day"].date() == d.date():
                        new_day_items.append({'day': d, 'sum': i["sum"]})
    new_day_items.reverse()
    # Weekly
    week_items = Payment.objects.annotate(
        week_num=ExtractWeek('timestamp')   # sets week number for each row
    ).values(
        'week_num'
    ).annotate(
        sum=Sum('amount')
    )
    new_week_item = []
    week_no = datetime.now().isocalendar()[1]
    for i in range(1,week_no + 1):
        found = False
        for item in week_items:
            if item["week_num"] == i:
                new_week_item.append(item)
                found = True
        if found == False:
            temp_dict = {}
            temp_dict["week_num"] = i
            temp_dict["sum"] = 0
            new_week_item.append(temp_dict)
    # Monthly
    month_item = Payment.objects.annotate(
        month=ExtractMonth('timestamp')
    ).values(
        'month'
    ).annotate(
        sum=Sum('amount')
    )
    new_month_item = []
    for i in range(1,datetime.now().month + 1):
        found = False
        for item in month_item:
            if item["month"] == i:
                item["month"] = calendar.month_name[i]
                new_month_item.append(item)
                found = True
        if found == False:
            temp_dict = {}
            temp_dict["month"] = calendar.month_name[i]
            temp_dict["sum"] = 0
            new_month_item.append(temp_dict)
    return render(request, 'admin/payment_charts.html', {"day_dataset":new_day_items, "week_dataset":new_week_item, "month_dataset":new_month_item})


@staff_member_required
def subscription_graph_view(request):
    day_items = SubscriptionPayment.objects.annotate(day=TruncDay('timestamp')).values('day').annotate(sum=Sum('price')).values('day', 'sum')
    day_items = list(day_items)
    dates = [x.get('day').date() for x in day_items]
    new_day_items = []
    if request.method == 'POST':
        datetime_object = datetime.strptime(request.POST['date'], '%m/%d/%Y')
        for d in (datetime_object - timedelta(days=x) for x in range(0,30)):
            if d.date() not in dates:
                new_day_items.append({'day': d, 'sum': 0})
            else:
                for i in day_items:
                    if i["day"].date() == d.date():
                        new_day_items.append({'day': d, 'sum': i["sum"]})
    else:
        for d in (datetime.today() - timedelta(days=x) for x in range(0,30)):
            if d.date() not in dates:
                new_day_items.append({'day': d, 'sum': 0})
            else:
                for i in day_items:
                    if i["day"].date() == d.date():
                        new_day_items.append({'day': d, 'sum': i["sum"]})
    # for d in (datetime.today() - timedelta(days=x) for x in range(0,30)):
    #     if d.date() not in dates:
    #         new_day_items.append({'day': d, 'sum': 0})
    #     else:
    #         for i in day_items:
    #             if i["day"].date() == d.date():
    #                 new_day_items.append({'day': d, 'sum': i["sum"]})
    new_day_items.reverse()
    # Weekly
    week_items = SubscriptionPayment.objects.annotate(
        week_num=ExtractWeek('timestamp')   # sets week number for each row
    ).values(
        'week_num'
    ).annotate(
        sum=Sum('price')
    )
    new_week_item = []
    week_no = datetime.now().isocalendar()[1]
    for i in range(1,week_no + 1):
        found = False
        for item in week_items:
            if item["week_num"] == i:
                new_week_item.append(item)
                found = True
        if found == False:
            temp_dict = {}
            temp_dict["week_num"] = i
            temp_dict["sum"] = 0
            new_week_item.append(temp_dict)
    # Monthly
    month_item = SubscriptionPayment.objects.annotate(
        month=ExtractMonth('timestamp')
    ).values(
        'month'
    ).annotate(
        sum=Sum('price')
    )
    new_month_item = []
    for i in range(1,datetime.now().month + 1):
        found = False
        for item in month_item:
            if item["month"] == i:
                item["month"] = calendar.month_name[i]
                new_month_item.append(item)
                found = True
        if found == False:
            temp_dict = {}
            temp_dict["month"] = calendar.month_name[i]
            temp_dict["sum"] = 0
            new_month_item.append(temp_dict)
    return render(request, 'admin/subscription_charts.html', {"day_dataset":new_day_items, "week_dataset":new_week_item, "month_dataset":new_month_item})
    
