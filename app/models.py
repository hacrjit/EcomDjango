from django.db import models
from django.contrib.auth.models import User

# Create your models here.

CATEGORY_CHOICES = (
    ("CD", "Curd"),
    ("ML", "Milk"),
    ("MS", "Milkshake"),
    ("PN", "Paneer"),
    ("GH", "Ghee"),
    ("CZ", "Cheese"),
    ("IC", "Ice Cream"),
    ("LS", "Lassi"),
)

STATE_CHOICES = (
    # add for india
    ("AP", "Andhra Pradesh"),
    ("AR", "Arunachal Pradesh"),
    ("AS", "Assam"),
    ("BR", "Bihar"),
    ("CT", "Chhattisgarh"),
    ("GA", "Goa"),
    ("GJ", "Gujarat"),
    ("HR", "Haryana"),
    ("HP", "Himachal Pradesh"),
    ("JK", "Jammu and Kashmir"),
    ("JH", "Jharkhand"),
    ("KA", "Karnataka"),
    ("KL", "Kerala"),
    ("MP", "Madhya Pradesh"),
    ("MH", "Maharashtra"),
    ("MN", "Manipur"),
    ("ML", "Meghalaya"),
    ("MZ", "Mizoram"),
    ("NL", "Nagaland"),
    ("OR", "Odisha"),
    ("PB", "Punjab"),
    ("RJ", "Rajasthan"),
    ("SK", "Sikkim"),
    ("TN", "Tamil Nadu"),
    ("TG", "Telangana"),
    ("TR", "Tripura"),
    ("UT", "Uttarakhand"),
    ("UP", "Uttar Pradesh"),
    ("WB", "West Bengal"),
    ("AN", "Andaman and Nicobar Islands"),
    ("CH", "Chandigarh"),
    ("DN", "Dadra and Nagar Haveli and Daman and Diu"),
    ("DL", "Delhi"),
    ("LD", "Lakshadweep"),
    ("PY", "Puducherry"),
)

class Product(models.Model):
    title = models.CharField(max_length=100)
    selling_price = models.FloatField()
    discounted_price = models.FloatField()
    description = models.TextField()
    composition = models.TextField(default="")
    prodapp = models.TextField(default="")
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    product_image = models.ImageField(upload_to='product')
    def __str__(self):
        return self.title

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    mobile = models.CharField(max_length=15)
    zipcode = models.IntegerField()
    state = models.CharField(choices=STATE_CHOICES, max_length=50)
    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    checked_out = models.BooleanField(default=False)
    
    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price
    
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    razorpay_order_id = models.CharField(max_length=500,blank=True,null=True)
    razorpay_payment_status = models.CharField(max_length=500,blank=True,null=True)
    razorpay_payment_id = models.CharField(max_length=500,blank=True,null=True)
    paid = models.BooleanField(default=False)


class OrderPlaced(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices= (("Accepted", "Accepted"), ("Packed", "Packed"), ("On The Way", "On The Way"), ("Delivered", "Delivered")), default="Pending")
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, default="")
    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price