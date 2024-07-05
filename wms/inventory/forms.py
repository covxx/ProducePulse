from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Category, InventoryItem, ItemImages, Customer
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.forms.utils import flatatt
from django.core.exceptions import ValidationError
import os

def validate_image_file(file):
    valid_mime_types = ['image/jpeg', 'image/png', 'image/gif']
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    max_file_size = 5 * 1024 * 1024  # 5MB

    # Validate MIME type
    if file.content_type not in valid_mime_types:
        raise ValidationError('Unsupported file type.')

    # Validate file extension
    ext = os.path.splitext(file.name)[1]
    if ext.lower() not in valid_extensions:
        raise ValidationError('Unsupported file extension.')

    # Validate file size
    if file.size > max_file_size:
        raise ValidationError('File size exceeds limit (5MB).')

class MultipleFileInput(forms.ClearableFileInput):
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = []
        final_attrs = self.build_attrs(attrs, {'type': self.input_type, 'name': name})
        return format_html('<input{} multiple>', flatatt(final_attrs))

class InventoryItemForm(forms.ModelForm):
    date_complained = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control datepicker'}),
        help_text="Select the date the complaint was made."
    )
    date_built = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control datepicker'}),
        help_text="Select the date the item was built."
    )
    class Meta:
        model = InventoryItem
        fields = ['customer', 'date_complained','complaint', 'category', 'date_built', 'built_by']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.all()
        self.fields['customer'].empty_label = "Select A Customer"
class ItemImagesForm(forms.ModelForm):
    images = forms.FileField(
        widget=MultipleFileInput(attrs={'accept': 'image/*'}), 
        required=False, 
        validators=[validate_image_file]
    )

    class Meta:
        model = ItemImages
        fields = ['images']
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']