from django.urls import path, include
from .import views

urlpatterns = [
    path('registeruser/', views.registeruser, name='registeruser'),
    path('register_restaurant/', views.register_restaurant, name='register_restaurant'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('myaccount/', views.myaccount, name='myaccount'),
    path('custdashboard/', views.custdashboard, name='custdashboard'),
    path('vendordashboard/', views.vendordashboard, name='vendordashboard'),

]
