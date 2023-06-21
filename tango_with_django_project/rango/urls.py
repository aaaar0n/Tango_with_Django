from django.urls import path

from rango.views import about
from rango.views import category
from rango.views import index
from rango.views import test
from rango.views import add_category


urlpatterns = [
    path('', index, name='index'),
    path('about/', about, name='about'),
    path('test/', test, name='test'),
    path('category/<str:category_name_url>/', category, name='category'),
    path('category/<category_name_slug>/', views.category, name='category'),
]
