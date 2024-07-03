from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Category, InventoryItem

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']  
    
class InventoryItemForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), initial=0) 
    class Meta:
        model = InventoryItem
        fields = ['name', 'complaint', 'date_complained','built_by', 'date_built', 'category'] 
    # Want to add a cost field and image uploading. Need to clean up the form view under item_form.html