from django.contrib import admin
from .models import Cart, OrderPlaced, Payment, Product,Customer

# Register your models here.

@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['id','title', 'selling_price', 'discounted_price', 'category']

@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ['id','user', 'name', 'locality', 'city', 'zipcode', 'state']

@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ['id','user', 'product', 'quantity', 'total_cost']

@admin.register(Payment)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = ['id','user', 'amount', 'razorpay_order_id', 'razorpay_payment_status', 'razorpay_payment_id', 'paid']

@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display = ['id','user', 'customer', 'product', 'quantity', 'ordered_date', 'status', 'payment', 'total_cost']