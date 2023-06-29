from django.urls import path

from rango.views import *

urlpatterns = [
    path('', index, name='index'),
    path('about/', about, name='about'),
    path('category/<str:category_name_url>/', category, name='category'),
    path('category/<str:category_name_url>/add_page/', add_page, name='add_page'),
    path('add_category/', add_category, name='add_category'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('restricted/', restricted, name='restricted'),
    path('logout/', user_logout, name='logout'),
    path('search/', search_view, name='search'),
]
