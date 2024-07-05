from django.contrib import admin
from django.urls import path
from . import views
from .views import Index, SignUpView, Dashboard, AddItem, EditItem, DeleteItem, item_detail, ReportsView, export_csv, export_excel
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
    path('item/<int:pk>/', views.item_detail , name='detail-item'), 
    path('reports/', ReportsView.as_view(), name='reports'),
    path('export/csv/', export_csv, name='export_csv'),
    path('export/excel/', export_excel, name='export_excel'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)