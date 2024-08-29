from django.contrib import admin
from django.urls import path
from . import views
from .views import Index, SignUpView, cDashboard, AddItem, EditItem, DeleteItem, item_detail, generate_report, CreateOrderView, CreateOrderCustomerView, OrderCustomerListView, EditOrderCustomerView, ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView,  CustomerProductPriceListView, OrderCustomerProductPriceCreateView, OrderCustomerProductPriceUpdateView, OrderCustomerProductPriceDeleteView, update_profile, change_password, get_product_unit, order_history, OrderEditView, FulfillmentListView, FulfillOrderView, OrderCustomerProductPriceDeleteView, VendorListView, VendorCreateView, VendorUpdateView, VendorDeleteView, ReceiveProductView, ReceiptView, LotListView, LotDetailView, StatusPageView
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('create_order/', CreateOrderView.as_view(), name="create_order"),
    path('dashboard/', cDashboard.as_view(), name="dashboard"),
    path('cdashboard/', cDashboard.as_view(), name="cdashboard"),
    path('add-item/', AddItem.as_view(), name="add-item"),
    path('edit-item/<int:pk>', EditItem.as_view(), name='edit-item'),
    path('delete-item/<int:pk>', DeleteItem.as_view(), name='delete-item'),
    path('signup/', SignUpView.as_view(), name="signup"),
    path('login/', auth_views.LoginView.as_view(template_name="inventory/login.html"), name="login"),
    path('logout/', auth_views.LogoutView.as_view(template_name="inventory/logout.html"), name='logout'),
    path('item/<int:pk>/', views.item_detail , name='detail-item'), 
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('generate_report/', generate_report, name='generate_report'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('add_customer/', CreateOrderCustomerView.as_view(), name='add_customer'),
    path('customers/', OrderCustomerListView.as_view(), name='order_customer_list'),
    path('edit_customer/<int:pk>/', EditOrderCustomerView.as_view(), name='edit_customer'),
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/add/', ProductCreateView.as_view(), name='product_create'),
    path('products/edit/<int:pk>/', ProductUpdateView.as_view(), name='product_edit'),
    path('products/delete/<int:pk>/', ProductDeleteView.as_view(), name='product_delete'),
    path('customer-product-prices/', CustomerProductPriceListView.as_view(), name='customer_product_price_list'),
    path('customer-product-prices/add/', OrderCustomerProductPriceCreateView.as_view(), name='customer_product_price_create'),
    path('customer-product-prices/edit/<int:pk>/', OrderCustomerProductPriceUpdateView.as_view(), name='customer_product_price_edit'),
    path('customer-product-prices/delete/<int:pk>/', OrderCustomerProductPriceDeleteView.as_view(), name='customer_product_price_delete'),
    path('get-product-unit/<int:product_id>/', get_product_unit, name='get_product_unit'),
    path('order/edit/<int:pk>/', OrderEditView.as_view(), name='order_edit'),
    path('order-history/', order_history, name='order_history'),
    path('fulfillment/', FulfillmentListView.as_view(), name='fulfillment_list'),
    path('fulfillment/<int:pk>/', FulfillOrderView.as_view(), name='fulfill_order'),
    path('vendors/', VendorListView.as_view(), name='vendor_list'),
    path('vendors/new/', VendorCreateView.as_view(), name='vendor_create'),
    path('vendors/edit/<int:pk>/', VendorUpdateView.as_view(), name='vendor_update'),
    path('vendors/delete/<int:pk>/', VendorDeleteView.as_view(), name='vendor_delete'),
    path('receive-product/', ReceiveProductView.as_view(), name='receive_product'),
    path('receipt/<int:pk>/', ReceiptView.as_view(), name='receipt'),
    path('product/<int:product_id>/lots/', LotListView.as_view(), name='lot_list'),
    path('lots/<int:pk>/', LotDetailView.as_view(), name='lot_detail'),
    path('js/', LotDetailView.as_view(), name='lot_detail'),
    path('status/', StatusPageView.as_view(), name='status_page'),



]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)