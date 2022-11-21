from django.urls import path, include
from .import views

urlpatterns = [
    path('registeruser/', views.registeruser, name='registeruser'),
    path('register_restaurant/', views.register_restaurant, name='register_restaurant'),

]
