from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from datetime import datetime
import os
import uuid
#Order system START

class Product(models.Model):
    UNIT_CHOICES = [
        ('cases', 'Cases'),
        ('pounds', 'Pounds'),
    ]

    name = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='cases')  # Default value added


    def __str__(self):
        return f"{self.name} ({self.get_unit_display()})"

class OrderCustomer(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    delivery_address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

class OrderCustomerProductPrice(models.Model):
    order_customer = models.ForeignKey(OrderCustomer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('order_customer', 'product')

    def __str__(self):
        return f"{self.order_customer.name} - {self.product.name}: ${self.price}"


class CustomerProductPrice(models.Model):
    order_customer = models.ForeignKey(OrderCustomer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('order_customer', 'product')

    def __str__(self):
        return f"{self.order_customer.name} - {self.product.name}: ${self.price}"

class Order(models.Model):
    order_number = models.CharField(max_length=12, unique=True, editable=False, default=uuid.uuid4().hex[:12])
    order_customer = models.ForeignKey(OrderCustomer, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    purchase_order_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_number} - {self.order_customer.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=10, choices=[('cases', 'Cases'), ('pounds', 'Pounds')])

    def __str__(self):
        return f"{self.product.name} - {self.quantity} {self.unit} in Order {self.order.order_number}"
#Order system END
def upload_to(instance, filename):
    base, ext = os.path.splitext(filename)
    new_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
    return os.path.join('item_images', new_filename)
class Customer(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
class InventoryItem(models.Model):
    STATUS_CHOICES = [ # For Status Tagging Syste,
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('waiting', 'Waiting'),
        ('closed', 'Closed')
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='inventory_items', null=True, blank=True) #Customer field dropdown
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New') #For status tagging system
    name = models.CharField(default="Enter Customer Name...", max_length=200) #Old cs name field
    complaint = models.TextField(max_length=2000, default="Enter Complaint...")
    date_complained = models.CharField(max_length=10, default="MM/DD/YYYY") #Date picker field for complained date
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, blank=True, null=True) #Category dropdown
    date_created = models.DateField(auto_now_add=True) #Date created field, is timestamped
    date_built = models.CharField(max_length=10, default="MM/DD/YYYY") #Date picker field for built date
    built_by = models.CharField(max_length=200, default="Enter Builder Name...") #Builder name field, text input
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING) #User field, auto stamped

    def append_complaint(self, new_complaint, User): #Function to append new complaint to existing complaint with timestamp, apart of the 'updates' system
        timestamp = datetime.now().strftime('%m-%d-%Y %H:%M')
        self.complaint += f"\n[{timestamp}] ({User.username}): {new_complaint}"
        self.save()

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=200)
    class Meta:
        verbose_name_plural = 'Categories'
    def __str__(self):
        return self.name
class ItemImages(models.Model):
    item = models.ForeignKey(InventoryItem, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_to)