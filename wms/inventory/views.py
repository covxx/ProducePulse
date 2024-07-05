# views.py
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, CreateView, UpdateView, DeleteView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from .forms import UserRegisterForm, InventoryItemForm, ItemImagesForm
from .models import InventoryItem, Category, ItemImages
from django.core.exceptions import ValidationError
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

# Get an instance of a logger
logger = logging.getLogger(__name__)

def validate_image_file(file):
    valid_mime_types = ['image/jpeg', 'image/png', 'image/gif']
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    max_file_size = 5 * 1024 * 1024  # 5MB

    if file.content_type not in valid_mime_types:
        raise ValidationError('Unsupported file type.')

    ext = os.path.splitext(file.name)[1]
    if ext.lower() not in valid_extensions:
        raise ValidationError('Unsupported file extension.')

    if file.size > max_file_size:
        raise ValidationError('File size exceeds limit (5MB).')

class Index(TemplateView):
    template_name = 'inventory/index.html'

class Dashboard(LoginRequiredMixin, View):
    def get(self, request):
        items = InventoryItem.objects.all().order_by('id')
        logger.debug('Dashboard view accessed by user: %s', request.user)
        return render(request, 'inventory/dashboard.html', {'items': items})

def item_detail(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    images = ItemImages.objects.filter(item=item)
    
    if request.method == 'POST':
        images_form = ItemImagesForm(request.POST, request.FILES)
        
        if images_form.is_valid():
            uploaded_images = request.FILES.getlist('images')
            for image in uploaded_images:
                ItemImages.objects.create(item=item, image=image)
            logger.info('Images uploaded for item ID: %s', item.id)
            return redirect('detail-item', pk=item.pk)
        else:
            logger.error('Image upload failed for item ID: %s', item.id)
            return render(request, 'inventory/item_detail.html', {
                'images_form': images_form,
                'item': item,
                'images': images,
                'image_errors': images_form.errors
            })
    else:
        images_form = ItemImagesForm()

    return render(request, 'inventory/item_detail.html', {
        'images_form': images_form,
        'item': item,
        'images': images
    })

class SignUpView(View):
    def get(self, request):
        form = UserRegisterForm()
        return render(request, 'inventory/signup.html', {'form': form})

    def post(self, request):
        form = UserRegisterForm(request.POST)
        
        if form.is_valid():
            form.save()
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            login(request, user)
            logger.info('New user signed up: %s', user.username)
            return redirect('index')
        logger.error('Sign up failed for data: %s', form.errors)
        return render(request, 'inventory/signup.html', {'form': form})

class AddItem(LoginRequiredMixin, CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('dashboard')
    title = "Add Customer Complaint"
    submit_button_text = "Add Item"

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        
        uploaded_images = self.request.FILES.getlist('images')
        for image in uploaded_images:
            validate_image_file(image)
            ItemImages.objects.create(item=self.object, image=image)
        logger.info('New item added with ID: %s', self.object.id)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['title'] = self.title
        context['submit_button_text'] = self.submit_button_text
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images_form'] = ItemImagesForm()
        context['categories'] = Category.objects.all()
        return context

class EditItem(LoginRequiredMixin, UpdateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class DeleteItem(LoginRequiredMixin, DeleteView):
    model = InventoryItem
    template_name = 'inventory/delete_item.html'
    success_url = reverse_lazy('dashboard')
    context_object_name = 'item'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        logger.info('Item deleted with ID: %s', self.object.id)
        return response

class ReportsView(LoginRequiredMixin, View):
    def get(self, request):
        # Gather data for reports
        items = InventoryItem.objects.all()
        data = pd.DataFrame(list(items.values('date_complained', 'category')))

        # Generate charts
        bar_chart = self.generate_bar_chart(data)
        pie_chart = self.generate_pie_chart(data)

        return render(request, 'inventory/reports.html', {
            'bar_chart': bar_chart,
            'pie_chart': pie_chart,
        })

    def generate_bar_chart(self, data):
        plt.figure(figsize=(10, 6))
        data['category'].value_counts().plot(kind='bar')
        plt.title('Complaints by Category')
        plt.xlabel('Category')
        plt.ylabel('Count')

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()

        graphic = base64.b64encode(image_png)
        graphic = graphic.decode('utf-8')

        return graphic

    def generate_pie_chart(self, data):
        plt.figure(figsize=(8, 8))
        data['category'].value_counts().plot(kind='pie', autopct='%1.1f%%')
        plt.title('Complaints Distribution by Category')

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()

        graphic = base64.b64encode(image_png)
        graphic = graphic.decode('utf-8')

        return graphic

def export_csv(request):
    items = InventoryItem.objects.all()
    data = pd.DataFrame(list(items.values()))
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=report.csv'
    data.to_csv(path_or_buf=response, index=False)
    return response

def export_excel(request):
    items = InventoryItem.objects.all()
    data = pd.DataFrame(list(items.values()))
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=report.xlsx'
    data.to_excel(response, index=False)
    return response