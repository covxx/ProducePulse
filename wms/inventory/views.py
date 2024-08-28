import logging, os
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.forms import inlineformset_factory
from .forms import UserRegisterForm, InventoryItemForm, ItemImagesForm, UserProfileForm, SearchForm, ReportForm, OrderForm, OrderItemForm, OrderCustomerForm, ProductForm, CustomerProductPrice, OrderCustomerProductPrice, OrderForm, OrderItemFormSetFactory, OrderItemFulfillmentFormSetFactory, VendorForm, ReceiveProductForm, LotFormSet
from .models import InventoryItem, Category, ItemImages, Order, OrderItem, OrderCustomer, Product, CustomerProductPrice, OrderCustomerProductPrice, Order, OrderItem, OrderItemLot, Lot, Vendor
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.db.models import Q
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from datetime import datetime
from django.contrib.auth import views as auth_views

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
        raise ValidationError('Unsupported file type.') # Raise an error if the file type is not supported``
    ext = os.path.splitext(file.name)[1]
    if ext.lower() not in valid_extensions:
        raise ValidationError('Unsupported file extension.')

    if file.size > max_file_size:
        raise ValidationError('File size exceeds limit (5MB).')

class cDashboard(LoginRequiredMixin, View):
    def get(self, request):
        form = SearchForm()
        query = request.GET.get('query')
        if query:
            items = InventoryItem.objects.filter(
                Q(name__icontains=query) | Q(complaint__icontains=query) | Q(category__name__icontains=query) | Q(built_by__icontains=query)
            )
        else:
            items = InventoryItem.objects.all()
        return render(request, 'inventory/cdashboard.html', {'items': items, 'form': form})

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
class CustomPasswordResetView(auth_views.PasswordResetView):
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    template_name = 'password_reset_form.html'
    success_url = reverse_lazy('password_reset_done')
    
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
    
class ReceiveProductView(View):
    def get(self, request):
        form = ReceiveProductForm()
        return render(request, 'inventory/receive_product.html', {'form': form})

    def post(self, request):
        form = ReceiveProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('receive_product')  # Redirect back to form for more entries or change to a receipt view
        return render(request, 'inventory/receive_product.html', {'form': form})

class AddItem(LoginRequiredMixin, CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('cdashboard')
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
    success_url = reverse_lazy('cdashboard')
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
    success_url = reverse_lazy('cdashboard')
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
#Order system STARTF
#OrderItemFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1)

class VendorListView(ListView):
    model = Vendor
    template_name = 'inventory/vendor_list.html'

class VendorCreateView(CreateView):
    model = Vendor
    form_class = VendorForm
    template_name = 'inventory/vendor_form.html'
    success_url = reverse_lazy('vendor_list')

class VendorUpdateView(UpdateView):
    model = Vendor
    form_class = VendorForm
    template_name = 'inventory/vendor_form.html'
    success_url = reverse_lazy('vendor_list')

class VendorDeleteView(DeleteView):
    model = Vendor
    template_name = 'inventory/vendor_confirm_delete.html'
    success_url = reverse_lazy('vendor_list')

class CreateOrderView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'inventory/create_order.html'
    success_url = reverse_lazy('order_history')

    def form_valid(self, form):
        form.instance.created_by = self.request.user  # Set the created_by field to the logged-in user
        context = self.get_context_data()
        orderitem_formset = context['orderitem_formset']

        if orderitem_formset.is_valid():
            if 'submit_order' in self.request.POST:
                form.instance.is_submitted = True  # Mark the order as submitted

            # Save the form and the related order items
            self.object = form.save()
            orderitem_formset.instance = self.object
            orderitem_formset.save()

            return super().form_valid(form)
        else:
            # If the formset is not valid, re-render the form with the errors
            return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['orderitem_formset'] = OrderItemFormSetFactory(self.request.POST, instance=self.object)
        else:
            data['orderitem_formset'] = OrderItemFormSetFactory(instance=self.object)
        return data
        
class OrderCustomerProductPriceForm(forms.ModelForm):
    class Meta:
        model = OrderCustomerProductPrice
        fields = ['order_customer', 'product', 'price']
        widgets = {
            'order_customer': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class OrderCustomerProductPriceListView(ListView):
    model = OrderCustomerProductPrice
    template_name = 'inventory/order_customer_product_price_list.html'
    context_object_name = 'order_customer_product_prices'

class OrderCustomerProductPriceCreateView(CreateView):
    model = OrderCustomerProductPrice
    form_class = OrderCustomerProductPriceForm
    template_name = 'inventory/order_customer_product_price_form.html'
    success_url = reverse_lazy('order_customer_product_price_list')

class OrderCustomerProductPriceUpdateView(UpdateView):
    model = OrderCustomerProductPrice
    form_class = OrderCustomerProductPriceForm
    template_name = 'inventory/order_customer_product_price_form.html'
    success_url = reverse_lazy('order_customer_product_price_list')

class OrderCustomerProductPriceDeleteView(DeleteView):
    model = OrderCustomerProductPrice
    template_name = 'inventory/order_customer_product_price_confirm_delete.html'
    success_url = reverse_lazy('order_customer_product_price_list')

class CustomerProductPriceListView(ListView):
    model = CustomerProductPrice
    template_name = 'inventory/customer_product_price_list.html'
    context_object_name = 'customer_product_prices'

class ProductListView(ListView):
    model = Product
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('product_list')

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('product_list')

class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'inventory/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')

class OrderHistoryView(ListView):
    model = Order
    template_name = 'inventory/order_history.html'

    def get_queryset(self):
        return Order.objects.filter(order_customer=self.kwargs['customer_id']).order_by('-created_at')

class CreateOrderCustomerView(CreateView):
    model = OrderCustomer
    form_class = OrderCustomerForm
    template_name = 'inventory/create_order_customer.html'
    success_url = reverse_lazy('order_customer_list')

class OrderCustomerListView(ListView):
    model = OrderCustomer
    template_name = 'inventory/order_customer_list.html'
    context_object_name = 'customers'

class EditOrderCustomerView(UpdateView):
    model = OrderCustomer
    form_class = OrderCustomerForm
    template_name = 'inventory/edit_order_customer.html'
    success_url = reverse_lazy('order_customer_list')

def get_product_unit(request, product_id):
    product = Product.objects.get(pk=product_id)
    return JsonResponse({'unit': product.unit})

def order_history(request):
    orders_list = Order.objects.all().order_by('-created_at')
    paginator = Paginator(orders_list, 10)  # Show 10 orders per page

    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)

    context = {
        'orders': orders
    }
    return render(request, 'inventory/order_history.html', context)
class OrderEditView(UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'inventory/edit_order.html'
    success_url = reverse_lazy('order_history')

    def form_valid(self, form):
        context = self.get_context_data()
        orderitem_formset = context['orderitem_formset']
        if orderitem_formset.is_valid():
            if 'submit_order' in self.request.POST:
                form.instance.is_submitted = True  # Mark the order as submitted
            # Save the form and the related order items
                self.object = form.save()
                orderitem_formset.instance = self.object
                orderitem_formset.save()
                return super().form_valid(form)
        else:
            # If the formset is not valid, re-render the form with the errors
            return self.render_to_response(self.get_context_data(form=form))
            
#Order system END
#FullFillment system START

class FulfillmentListView(View):
    def get(self, request):
        orders = Order.objects.filter(is_submitted=True).order_by('created_at')
        return render(request, 'inventory/fulfillment_list.html', {'orders': orders})

class FulfillOrderView(View):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        order_items = OrderItem.objects.filter(order=order)
        print("Order Items:", order_items)  # Debugging: Print the queryset to console

        orderitem_formset = OrderItemFulfillmentFormSetFactory(queryset=order_items)
        return render(request, 'inventory/fulfill_order.html', {
            'order': order,
            'orderitem_formset': orderitem_formset
        })

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        order_items = OrderItem.objects.filter(order=order)
        orderitem_formset = OrderItemFulfillmentFormSetFactory(request.POST, queryset=order_items)
        
        if orderitem_formset.is_valid():
            orderitem_formset.save()
            return redirect('fulfillment_list')
        
        return render(request, 'inventory/fulfill_order.html', {
            'order': order,
            'orderitem_formset': orderitem_formset
        })

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        orderitem_formset = OrderItemFulfillmentFormSetFactory(request.POST, instance=order)
        if orderitem_formset.is_valid():
            orderitem_formset.save()
            return redirect('fulfillment_list')
        return render(request, 'inventory/fulfill_order.html', {
            'order': order,
            'orderitem_formset': orderitem_formset
        })
    
class ReceiptView(View):
    def get(self, request, pk):
        lot = get_object_or_404(Lot, pk=pk)
        return render(request, 'inventory/receipt.html', {'lot': lot})

class ReceiveProductView(View):
    def get(self, request):
        vendor_form = ReceiveProductForm()
        formset = LotFormSet(queryset=Lot.objects.none())  # Start with an empty formset
        return render(request, 'inventory/receive_product.html', {
            'vendor_form': vendor_form,
            'formset': formset
        })

    def post(self, request):
        vendor_form = ReceiveProductForm(request.POST)
        formset = LotFormSet(request.POST)

        if vendor_form.is_valid() and formset.is_valid():
            vendor = vendor_form.cleaned_data['vendor']
            instances = formset.save(commit=False)
            for instance in instances:
                instance.vendor = vendor  # Set the vendor for each lot based on the selected vendor
                instance.lot_number = Lot.generate_lot_number()  # Automatically generate the lot number
                instance.save()
            return redirect('receive_product')  # Redirect back to form for more entries or change to a receipt view

        return render(request, 'inventory/receive_product.html', {
            'vendor_form': vendor_form,
            'formset': formset
        })
class LotListView(ListView):
    model = Lot
    template_name = 'inventory/lot_list.html'
    context_object_name = 'lots'

    def get_queryset(self):
        self.product = get_object_or_404(Product, pk=self.kwargs['product_id'])
        return Lot.objects.filter(product=self.product)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context

class LotDetailView(DetailView):
    model = Lot
    template_name = 'inventory/lot_detail.html'
    context_object_name = 'lot'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movements'] = OrderItemLot.objects.filter(lot=self.object).order_by('-order_item__order__created_at')
        return context