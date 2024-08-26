from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, Submit
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Category, InventoryItem, ItemImages, Customer, Order, OrderItem, Customer, Product, OrderCustomer, CustomerProductPrice,OrderCustomerProductPrice, OrderItemLot 
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.forms.utils import flatatt
from django.core.exceptions import ValidationError
from django.forms.models import inlineformset_factory, BaseInlineFormSet
import os
import re

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
#Order system START
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'unit_price', 'unit']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_customer', 'purchase_order_number', 'build_date']  # Exclude 'order_number'
        widgets = {
            'build_date': forms.DateInput(attrs={'type': 'date'}),  # Date input for build date
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only check order_customer if the instance exists
        if self.instance and self.instance.pk:
            if self.instance.order_customer:
                self.fields['order_customer'].initial = self.instance.order_customer
        self.fields['order_customer'].required = True  # Ensure this field is required

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'unit']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].widget.attrs.update({'class': 'form-control'})
        self.fields['quantity'].widget.attrs.update({'class': 'form-control'})
        self.fields['unit'].widget.attrs.update({'class': 'form-control', 'readonly': 'readonly'})

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        if product:
            cleaned_data['unit'] = product.unit  # Automatically set the unit based on the product
        return cleaned_data

class OrderItemFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.order_customer = kwargs.pop('order_customer', None)
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.fields['product'].queryset = Product.objects.all()
            form.initial['order_customer'] = self.order_customer

OrderItemFormSetFactory = inlineformset_factory(
    Order, OrderItem, form=OrderItemForm, formset=OrderItemFormSet, extra=1
)
    
class CustomerProductPriceForm(forms.ModelForm):
    class Meta:
        model = CustomerProductPrice
        fields = ['order_customer', 'product', 'price']
        widgets = {
            'order_customer': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class OrderCustomerForm(forms.ModelForm):
    class Meta:
        model = OrderCustomer
        fields = ['name', 'address', 'phone_number', 'delivery_address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['address'].widget.attrs.update({'class': 'form-control'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control'})
        self.fields['delivery_address'].widget.attrs.update({'class': 'form-control'})

    def clean_address(self):
        address = self.cleaned_data.get('address')
        # Basic validation pattern (You can improve this pattern according to your requirements)
        if not re.match(r'^[0-9a-zA-Z\s,.-]+$', address):
            raise forms.ValidationError("Please enter a valid address.")
        return address

    def clean_delivery_address(self):
        delivery_address = self.cleaned_data.get('delivery_address')
        # Basic validation pattern (You can improve this pattern according to your requirements)
        if delivery_address and not re.match(r'^[0-9a-zA-Z\s,.-]+$', delivery_address):
            raise forms.ValidationError("Please enter a valid delivery address.")
        return delivery_address
#Order system END

class OrderItemFulfillmentForm(forms.ModelForm):
    class Meta:
        model = OrderItemLot
        fields = ['lot', 'quantity_used']

OrderItemFulfillmentFormSetFactory = inlineformset_factory(
    OrderItem,
    OrderItemLot,
    form=OrderItemFulfillmentForm,
    extra=1,
    can_delete=True
)