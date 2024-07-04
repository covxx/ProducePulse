from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, CreateView, UpdateView, DeleteView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegisterForm, InventoryItemForm, ItemImagesForm
from .models import InventoryItem, Category, ItemImages
from django.core.exceptions import ValidationError

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

class Index(TemplateView):
    template_name = 'inventory/index.html'

class Dashboard(LoginRequiredMixin, View):
    def get(self, request):
        items = InventoryItem.objects.all().order_by('id')  # Remove user filter
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
            return redirect('detail-item', pk=item.pk)
        else:
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
                return redirect('index')
        return render(request, 'inventory/signup.html', {'form': form})

def add_item(request):
    if request.method == 'POST':
        item_form = InventoryItemForm(request.POST)
        images_form = ItemImagesForm(request.POST, request.FILES)
        
        if item_form.is_valid():
            item = item_form.save(commit=False)
            item.user = request.user
            item.save()
            
            uploaded_images = request.FILES.getlist('images')
            errors = []
            for image in uploaded_images:
                try:
                    validate_image_file(image)
                    ItemImages.objects.create(item=item, image=image)
                except ValidationError as e:
                    errors.append(e.message)

            if errors:
                images_form.add_error('images', errors)

            if not errors:
                return redirect('dashboard')

        categories = Category.objects.all()
        return render(request, 'inventory/item_form.html', {
            'item_form': item_form,
            'images_form': images_form,
            'categories': categories,
        })
    else:
        item_form = InventoryItemForm()
        images_form = ItemImagesForm()
        categories = Category.objects.all()
        return render(request, 'inventory/item_form.html', {
            'item_form': item_form,
            'images_form': images_form,
            'categories': categories,
        })

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
