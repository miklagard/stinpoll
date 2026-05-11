# backend/backend/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'profiles', views.ProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='api-login'),
    path('logout/', views.logout_user, name='api-logout'),
    path('verify/<uuid:token>/', views.verify_email, name='verify'),
    path('set-password/<uuid:token>/', views.set_password_and_login, name='set-password'),
    path('delete-account/<uuid:token>/', views.delete_account, name='delete'),
    path('my-profile/', views.get_user_profile, name='my-profile'),
]