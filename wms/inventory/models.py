from django.db import models
from django.contrib.auth.models import User

class InventoryItem(models.Model):
    name = models.CharField(max_length=200, default="Enter Customer Name...")
    complaint = models.TextField(max_length=2000, default="Enter Complaint...")
    date_complained = models.CharField(max_length=10, default="MM/DD/YYYY")
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)
    date_built = models.CharField(max_length=10, default="MM/DD/YYYY")
    built_by = models.CharField(max_length=200, default="Enter Builder Name...")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)  # Assuming user is related to item creator

    # Add a ManyToManyField for storing multiple images
    images = models.ManyToManyField('ItemImages', blank=True)

    def __str__(self):
        return self.name
    
class ItemImages(models.Model):
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='item_images/')

    def __str__(self):
        return f"Image for {self.item.name}"
    
class Category(models.Model):
    name = models.CharField(max_length=200)
    class Meta:
        verbose_name_plural = 'Categories'
    def __str__(self):
        return self.name
   