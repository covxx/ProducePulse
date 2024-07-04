from django.contrib import admin
from django.urls import path
from . import views
from .views import Index, SignUpView, Dashboard, AddItem, EditItem, DeleteItem, item_detail
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('dashboard/', Dashboard.as_view(), name="dashboard"),
    path('add-item/', AddItem.as_view(), name="add-item"),
    path('edit-item/<int:pk>', EditItem.as_view(), name='edit-item'),
    path('delete-item/<int:pk>', DeleteItem.as_view(), name='delete-item'),
    path('signup/', SignUpView.as_view(), name="signup"),
    path('login/', auth_views.LoginView.as_view(template_name="inventory/login.html"), name="login"),
    path('logout/', auth_views.LogoutView.as_view(template_name="inventory/logout.html"), name='logout'),
    path('item/<int:pk>/', views.item_detail , name='detail-item'),  # Ensure this matches the redirect name
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)