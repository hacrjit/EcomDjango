from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
import razorpay
from .models import Cart, Customer, OrderPlaced, Payment, Product
from .forms import CustomerProfileForm, CustomerRegistrationForm
from django.contrib import messages
from django.contrib.auth import logout


# Create your views here.
def home(request):
    return render(request, 'app/home.html') # This will render the home.html file in the app/templates/app directory

def about(request):
    return render(request, 'app/about.html') # This will render the about.html file in the app/templates/app directory

def contact(request):
    return render(request, 'app/contact.html') # This will render the contact.html file in the app/templates/app directory

class CategoryView(View):
    def get(self, request, value):
        products = Product.objects.filter(category=value)
        title = Product.objects.filter(category=value).values('title')
        return render(request, 'app/category.html', locals())
    
class CategoryTitle(View):
    def get(self, request, value):
        product = Product.objects.filter(title=value)
        title = Product.objects.filter(category=product[0].category).values('title')
        return render(request, 'app/category.html', locals())

class ProductDetail(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        return render(request,"app/productdetail.html",locals())

class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        return render(request,"app/customerregistration.html",locals())
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request,'Congratulations!! Registered Successfully')
            form.save()
        else:
            messages.error(request,'Failed to Register')
        return render(request,"app/customerregistration.html",locals())
    
class ProfileView(View):
    def get(self,request):
        form = CustomerProfileForm()
        return render(request,"app/profile.html",locals()) # This will render the profile.html file in the app/templates/app directory

    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            zipcode = form.cleaned_data['zipcode']
            state = form.cleaned_data['state']
            reg = Customer(user=user,name=name,locality=locality,city=city,zipcode=zipcode,state=state)
            reg.save()
            messages.success(request,'Congratulations!! Profile Updated Successfully')
        else:
            messages.error(request,'Failed to Update Profile')
        return render(request,"app/profile.html",locals())

def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html',locals()) # This will render the address.html file in the app/templates/app directory


class updateAddress(View):
    def get(self,request,pk):
        add=Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request, 'app/updateAddress.html',locals())
    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add=Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.zipcode = form.cleaned_data['zipcode']
            add.state = form.cleaned_data['state']
            add.save()
            messages.success(request,'Congratulations!! Address Updated Successfully')
        else:
            messages.error(request,'Failed to Update Address')
        return redirect('address') # This will redirect to the address view function


def custom_logout(request):
    logout(request)
    return redirect('login') 


from django.contrib.auth.decorators import login_required

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('show_cart')

@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Logic for immediate purchase goes here
    # This could involve redirecting to a checkout page with the product details pre-filled
    return redirect('checkout', product_id=product.id)

def show_cart(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    return render(request, 'app/showcart.html',{'cart_items': cart_items}) # This will render the showcart.html file in the app/templates/app directory




@login_required
def update_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        try:
            quantity = int(request.POST.get('quantity'))
        except ValueError:
            return HttpResponseBadRequest("Invalid quantity")

        if quantity < 1:
            return HttpResponseBadRequest("Quantity must be at least 1")

        cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
        cart_item.quantity = quantity
        cart_item.save()
        return redirect('show_cart')
    else:
        return HttpResponseBadRequest("Invalid request method")

@login_required
def remove_from_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
        cart_item.delete()
    return redirect('show_cart')

@login_required
def show_cart(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    cart_total = sum(item.total_cost for item in cart_items)
    return render(request, 'app/showcart.html', locals())

@login_required
def checkout_view(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user, checked_out=False)
    cart_total = sum(item.total_cost for item in cart_items)
    famount = 0
    for item in cart_items:
        value = item.quantity * item.product.discounted_price
        famount += value
    totalamount = famount
    razorpay_amount = int(totalamount * 100)
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
    data = {
        'amount': razorpay_amount,
        'currency': 'INR',
        'receipt': 'order_rcptid_11',
    }
    payment_response = client.order.create(data=data)
    print(payment_response)
    order_id = payment_response['id']
    order_status = payment_response['status']
    if order_status == 'created':
        payment = Payment(user=user, amount=totalamount, razorpay_order_id=order_id,razorpay_payment_status=order_status)
        payment.save()
    return render(request, 'app/checkout.html', locals())


# def payment_done(request):
#     order_id = request.GET.get('order_id')
#     payment_id = request.GET.get('payment_id')
#     cust_id = request.GET.get('cust_id')
#     user = request.user
#     customer = Customer.objects.get(id=cust_id)
#     payment = Payment.objects.get(razorpay_order_id=order_id)
#     payment.paid = True
#     payment.razorpay_payment_id = payment_id
#     payment.save()
#     cart_items = Cart.objects.filter(user=user)
#     for item in cart_items:
#         OrderPlaced(user=user, customer=customer, product=item.product, quantity=item.quantity, payment=payment).save()
#         item.delete()

#     return redirect('orders')


def payment_done(request):
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    cust_id = request.GET.get('cust_id')
    user = request.user
    print(order_id, payment_id, cust_id)

    # Ensure the order_id, payment_id, and cust_id are provided
    if not order_id or not payment_id or not cust_id:
        return HttpResponseBadRequest("Missing required parameters")

    # Retrieve the Customer object or return a 404 error if it does not exist
    customer = get_object_or_404(Customer, id=cust_id)

    # Retrieve the Payment object or return a 404 error if it does not exist
    payment = get_object_or_404(Payment, razorpay_order_id=order_id)
    
    payment.paid = True
    payment.razorpay_payment_id = payment_id
    payment.save()

    cart_items = Cart.objects.filter(user=user)
    for item in cart_items:
        # Process each item in the cart (assuming you have some logic here)
        OrderPlaced(user=user, customer=customer, product=item.product, quantity=item.quantity, payment=payment).save()
        item.delete()

    return redirect('orders')
