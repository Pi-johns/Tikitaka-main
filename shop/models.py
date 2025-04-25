from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
import uuid

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default="")
    phone = models.BigIntegerField()
    city = models.CharField(null=True, max_length=20)
    state = models.CharField(null=True, max_length=20)
    profile_pic = models.ImageField(null=True, upload_to="customer_pic", default="userimg.png")
    token_used = models.BooleanField(default=False)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name


class Category(models.Model):
    category_name = models.CharField(max_length=50)

    def __str__(self):
        return self.category_name


TAG = (
    ('New', 'New'),
    ('Bestseller', 'Bestseller'),
    ('Trending', 'Trending'),
    ('Featured', 'Featured'),
    ('Sale', 'Sale'),
)


class Product(models.Model):
    product_name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(max_length=1000)
    brand = models.CharField(max_length=20, default="")
    price = models.IntegerField(default=0)
    tag = models.CharField(default="New", choices=TAG, max_length=20)
    stock = models.IntegerField(default=10)
    product_img = models.ImageField(upload_to="images")
    product_img1 = models.ImageField(upload_to="images")
    product_img2 = models.ImageField(upload_to="images")

    def __str__(self):
        return self.product_name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    qty = models.IntegerField()

    @property
    def price(self):
        return self.product.price

    @property
    def amount(self):
        if self.product is not None:
            return self.qty * self.product.price
        else:
            return 0

    def __str__(self):
        return self.product.product_name + " by " + self.user.email


STATUS = (
    ('Placed', 'Placed'),
    ('Confirmed', 'Confirmed'),
    ('Preparing', 'Preparing'),
    ('Shipped', 'Shipped'),
    ('Out For Delivery', 'Out For Delivery'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled'),
)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=10)
    last_name = models.CharField(max_length=10)
    phone = models.BigIntegerField(null=True)
    house_no = models.CharField(null=True, max_length=20)
    street = models.CharField(null=True, max_length=50)
    city = models.CharField(null=True, max_length=20)
    pin = models.IntegerField(null=True)
    state = models.CharField(null=True, max_length=20)
    total = models.FloatField()
    code = models.CharField(max_length=15, default="")
    placed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code + " to " + self.first_name + "\t" + self.last_name

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField()
    price = models.FloatField()
    amount = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS, default='Placed')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name + " by " + self.user.first_name

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, default="")
    subject = models.CharField(max_length=50)
    review = models.CharField(max_length=200)
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.product_name + " by " + self.customer.user.first_name


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_on = models.DateField(default=now, editable=False)

    def __str__(self):
        return self.user.first_name + " - " + self.product.product_name

STATUS = (
    (2, "failed"),
    (1, "Pending"),
    (0, "success")
)

class Transaction(models.Model):
    """This model records all the mpesa payment transactions"""
    transaction_no = models.CharField(default=uuid.uuid4, max_length=50, unique=True)
    phone_number = PhoneNumberField(null=False, blank=False,  max_length=15)
    checkout_request_id = models.CharField(max_length=200)
    reference = models.CharField(max_length=40, blank=True)
    description = models.TextField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2) 
    status = models.IntegerField(choices=STATUS, default=2)  # Changed to IntegerField
    receipt_no = models.CharField(max_length=200, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    ip = models.CharField(max_length=200, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, related_name='transactions')
    confirmed = models.BooleanField(default=False)  
    
    def __str__(self):
        return f"Transaction No: {self.transaction_no}, Amount: {self.amount}, Status: {self.get_status_display()}"

    def save(self, *args, **kwargs):
        # Calculate the total amount of the associated order and update the transaction amount
        if self.order:
            self.amount = int(self.order.total)
        super().save(*args, **kwargs)
        
class UserAction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50)  # e.g., 'viewed', 'purchased'
    timestamp = models.DateTimeField(auto_now_add=True)

