import logging, os
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, CreateView, UpdateView, DeleteView
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from .forms import UserRegisterForm, InventoryItemForm, ItemImagesForm, UserProfileForm, SearchForm, ReportForm
from .models import InventoryItem, Category, ItemImages
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.db.models import Q
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from datetime import datetime

# Get an instance of a logger
logger = logging.getLogger(__name__)

@login_required
def profile(request):
    return render(request, 'inventory/profile.html')

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'inventory/update_profile.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'inventory/change_password.html', {'form': form})

class Index(TemplateView):
    template_name = 'inventory/index.html'

def validate_image_file(file):
    valid_mime_types = ['image/jpeg', 'image/png', 'image/gif']
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf']
    max_file_size = 5 * 1024 * 1024  # 5MB

    if file.content_type not in valid_mime_types:
        raise ValidationError('Unsupported file type.')

    ext = os.path.splitext(file.name)[1]
    if ext.lower() not in valid_extensions:
        raise ValidationError('Unsupported file extension.')

    if file.size > max_file_size:
        raise ValidationError('File size exceeds limit (5MB).')

class Dashboard(LoginRequiredMixin, View):
    def get(self, request):
        form = SearchForm()
        query = request.GET.get('query')
        if query:
            items = InventoryItem.objects.filter(
                Q(name__icontains=query) | Q(complaint__icontains=query) | Q(category__name__icontains=query) | Q(built_by__icontains=query)
            )
        else:
            items = InventoryItem.objects.all()
        return render(request, 'inventory/dashboard.html', {'items': items, 'form': form})

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
    title = "Add New Complaint"
    submit_button_text = "Add Complaint"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.status = 'New'  # Ensure status is set to 'new'
        self.object.save()
        
        uploaded_images = self.request.FILES.getlist('images')
        for image in uploaded_images:
            validate_image_file(image)  # Validate the image file
            ItemImages.objects.create(item=self.object, image=image)
        
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['title'] = self.title
        context['submit_button_text'] = self.submit_button_text
        return context

class EditItem(LoginRequiredMixin, UpdateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('dashboard')
    submit_button_text = 'Save Complaint'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        additional_complaint = form.cleaned_data.get('additional_complaint')
        self.object.save()  # Save the object before calling append_complaint
        if additional_complaint:
            self.object.append_complaint(additional_complaint, self.request.user)
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['submit_button_text'] = self.submit_button_text
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
    
def generate_report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            built_by = form.cleaned_data['built_by']
            category = form.cleaned_data['category']

            items = InventoryItem.objects.filter(
                date_built__range=(start_date, end_date)
            )
            if built_by:
                items = items.filter(built_by=built_by)
            if category:
                items = items.filter(category=category)

            # Pagination
            paginator = Paginator(items, 10)  # Show 10 items per page
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            # Render the PDF template
            html_string = render_to_string('inventory/report_template.html', {
                'items': page_obj,
                'start_date': start_date,
                'end_date': end_date,
                'built_by': built_by,
                'category': category,
                'report_generated_on': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'user': request.user  # Pass the user information
            })
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="report.pdf"'

            # Create PDF
            pisa_status = pisa.CreatePDF(
                html_string, dest=response
            )
            if pisa_status.err:
                return HttpResponse('We had some errors with code %s' % pisa_status.err)
            return response
    else:
        form = ReportForm()

    return render(request, 'inventory/report_form.html', {'form': form})