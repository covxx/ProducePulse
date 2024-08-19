from django.contrib import admin
from django.urls import path
from . import views
from .views import Index, SignUpView, cDashboard, AddItem, EditItem, DeleteItem, item_detail, generate_report
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', Index.as_view(), name='index'),
   #path('dashboard/', Dashboard.as_view(), name="dashboard"),
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


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)