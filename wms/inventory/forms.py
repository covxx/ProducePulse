from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, Submit
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Category, InventoryItem, ItemImages, Customer
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.forms.utils import flatatt
from django.core.exceptions import ValidationError
import os

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

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
        widget=forms.TextInput(attrs={'class': 'form-control datepicker'})
    )
    date_built = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control datepicker'})
    )
    complaint = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Enter Complaint...'}),
        max_length=2000
    )
    built_by = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Builder Name...'}),
        max_length=50
    )
    cost = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Cost'}),
        required=False,
        max_digits=10,
        decimal_places=2
    )
    images = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        required=False,
        label='Upload Images'
    )
    additional_complaint = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add additional complaint...'}),
        max_length=1000,
        required=False
    )

    class Meta:
        model = InventoryItem
        fields = ['customer', 'date_complained', 'complaint', 'category', 'date_built', 'built_by', 'images', 'status']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.all()
        self.fields['customer'].empty_label = "Select A Customer"

        if 'instance' in kwargs and kwargs['instance'] is not None:
            # Edit mode: complaint field is uneditable and greyed out, status is editable
            self.fields['complaint'].widget.attrs['readonly'] = True
            self.fields['complaint'].widget.attrs['style'] = 'background-color: #e9ecef;'
            self.fields['status'] = forms.ChoiceField(
                choices=InventoryItem.STATUS_CHOICES,
                widget=forms.Select(attrs={'class': 'form-control'})
            )
        else:
            # Create mode: complaint field is editable, status is hidden
            self.fields['status'] = forms.CharField(
                widget=forms.HiddenInput(),
                initial='new'
            )
            self.fields.pop('additional_complaint')

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('customer', css_class='form-group col-md-3 mb-0'),
                Column('date_complained', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            'built_by',
            'complaint',
            'additional_complaint',  # Ensure additional_complaint is conditionally included
            'category',
            'date_built',
            'images',
            'status'  # Add status to the layout
        )

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

class SearchForm(forms.Form):
    query = forms.CharField(
        label='Search', 
        max_length=100, 
        widget=forms.TextInput(attrs={
            'class': 'form-control me-2', 
            'placeholder': 'Search complaints or items...'
        })
    )

class ReportForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control datepicker'}),
        label="Start Date"
    )
    end_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control datepicker'}),
        label="End Date"
    )
    built_by = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Builder Name...'}),
        label="Built By"
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Category"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('start_date', css_class='form-group col-md-3 mb-0'),
                Column('end_date', css_class='form-group col-md-3 mb-0'),
                Column('built_by', css_class='form-group col-md-3 mb-0'),
                Column('category', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Generate Report', css_class='btn btn-primary')
        )