from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from datetime import datetime
import os

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