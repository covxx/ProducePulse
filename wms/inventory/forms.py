from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Category, InventoryItem, ItemImages
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']  

class MultipleFileInput(forms.ClearableFileInput):
    def __init__(self, attrs=None):
        super().__init__(attrs=attrs)
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = []
        final_attrs = self.build_attrs(attrs, {'type': self.input_type})
        output = []
        for v in value:
            output.append('<li>%s</li>' % forms.FileInput().get_bound_field(name, value)[0])
        return mark_safe('<input%s multiple>' % format_html(forms.flatatt(final_attrs)))
class InventoryItemForm(forms.ModelForm):
    images = forms.FileField(widget=MultipleFileInput(attrs={'accept': 'image/*'}), required=False)

    class Meta:
        model = InventoryItem
        fields = ['name', 'complaint', 'date_complained', 'category', 'date_built', 'built_by']

    # Want to add a cost field and image uploading. Need to clean up the form view under item_form.html