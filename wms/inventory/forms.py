from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Category, InventoryItem, ItemImages
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.forms.utils import flatatt

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class MultipleFileInput(forms.ClearableFileInput):
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = []
        final_attrs = self.build_attrs(attrs, {'type': self.input_type, 'name': name})
        return format_html('<input{} multiple>', flatatt(final_attrs))

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['name', 'complaint', 'date_complained', 'category', 'date_built', 'built_by']

class ItemImagesForm(forms.ModelForm):
    images = forms.FileField(widget=MultipleFileInput(attrs={'accept': 'image/*'}), required=False)

    class Meta:
        model = ItemImages
        fields = ['images']
