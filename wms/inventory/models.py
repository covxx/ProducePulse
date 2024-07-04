from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from datetime import datetime
import os

def upload_to(instance, filename):
    base, ext = os.path.splitext(filename)
    new_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
    return os.path.join('item_images', new_filename)

class InventoryItem(models.Model):
    name = models.CharField(default="Enter Customer Name...", max_length=200)
    complaint = models.TextField(max_length=2000, default="Enter Complaint...")
    date_complained = models.CharField(max_length=10, default="MM/DD/YYYY")
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)
    date_built = models.CharField(max_length=10, default="MM/DD/YYYY")
    built_by = models.CharField(max_length=200, default="Enter Builder Name...")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)  # Probably should not happen
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