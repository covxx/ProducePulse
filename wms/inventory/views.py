from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, CreateView, UpdateView, DeleteView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegisterForm, InventoryItemForm, ItemImagesForm
from .models import InventoryItem, Category, ItemImages

class Index(TemplateView):
    template_name = 'inventory/index.html'

class Dashboard(LoginRequiredMixin, View):
    def get(self, request):
        items = InventoryItem.objects.filter(user=self.request.user.id).order_by('id')
        return render(request, 'inventory/dashboard.html', {'items': items})

def item_detail(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    images = ItemImages.objects.filter(item=item)
    
    if request.method == 'POST':
        item_form = InventoryItemForm(request.POST, instance=item)
        images_form = ItemImagesForm(request.POST, request.FILES)
        
        if item_form.is_valid():
            item_form.save()

        if images_form.is_valid():
            uploaded_images = request.FILES.getlist('images')
            for image in uploaded_images:
                ItemImages.objects.create(item=item, image=image)
            return redirect('detail-item', pk=item.pk)
    else:
        item_form = InventoryItemForm(instance=item)
        images_form = ItemImagesForm()

    return render(request, 'inventory/item_detail.html', {
        'item_form': item_form,
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

class AddItem(LoginRequiredMixin, View):
    def get(self, request):
        item_form = InventoryItemForm()
        images_form = ItemImagesForm()
        categories = Category.objects.all()
        return render(request, 'inventory/item_form.html', {'item_form': item_form, 'images_form': images_form, 'categories': categories})

    def post(self, request):
        item_form = InventoryItemForm(request.POST)
        images_form = ItemImagesForm(request.POST, request.FILES)
        
        if item_form.is_valid():
            item = item_form.save(commit=False)
            item.user = request.user
            item.save()
            
            if images_form.is_valid():
                uploaded_images = request.FILES.getlist('images')
                for image in uploaded_images:
                    ItemImages.objects.create(item=item, image=image)
            
            return redirect('dashboard')

        categories = Category.objects.all()
        return render(request, 'inventory/item_form.html', {'item_form': item_form, 'images_form': images_form, 'categories': categories})

class EditItem(LoginRequiredMixin, UpdateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('dashboard')

class DeleteItem(LoginRequiredMixin, DeleteView):
    model = InventoryItem
    template_name = 'inventory/delete_item.html'
    success_url = reverse_lazy('dashboard')
    context_object_name = 'item'
