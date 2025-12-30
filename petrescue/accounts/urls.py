from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),

    path('login/', views.login_view, name='login'),
    # Use a custom logout view so we can add a message and redirect to home
    path('logout/', views.logout_view, name='logout'),
]
