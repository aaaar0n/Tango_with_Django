from django.urls import path
from . import views

from rango.views import about
from rango.views import category
from rango.views import index
from rango.views import test, add_category
from rango.views import user_login


urlpatterns = [
    path('', index, name='index'),
    path('about/', about, name='about'),
    path('test/', test, name='test'),
    path('category/<str:category_name_url>/', category, name='category'),
    path('category/<str:category_name_slug>/', views.category, name='category'),
    path('add_category/', add_category, name='add_category'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
]
