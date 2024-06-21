from django.db import models
from django.contrib.auth.models import User

class InventoryItem(models.Model):
    name = models.CharField(default="Enter Customer Name...",max_length=200)
    complaint = models.TextField(max_length=2000,default="Enter Complaint...")
    date_complained = models.CharField(max_length=10,default="MM/DD/YYYY")
    #lot = models.IntegerField( )
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING) #Deletes inventory made by a user when the user is deleted, probably should not happen

    def __str__(self):
        return self.name
    
class Category(models.Model):
    name = models.CharField(max_length=200)
    class Meta:
        verbose_name_plural = 'Categories'
    def __str__(self):
        return self.name
   