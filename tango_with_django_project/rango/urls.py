from django.urls import path

from rango.views import about
from rango.views import category
from rango.views import index
from rango.views import add_category
from rango.views import user_login
from rango.views import register, restricted, user_logout


urlpatterns = [
    path('', index, name='index'),
    path('about/', about, name='about'),
    path('category/<str:category_name_url>/', category, name='category'),
    path('category/<str:category_name_slug>/', category, name='category'),
    path('add_category/', add_category, name='add_category'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('restricted/', restricted, name='restricted'),
    path('logout/', user_logout, name='logout'),
]
