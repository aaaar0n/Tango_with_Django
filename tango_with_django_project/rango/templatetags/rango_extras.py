from django import template
from rango.models import Category, Page

register = template.Library()

@register.inclusion_tag('rango/cats.html')
def get_category_list(cat=None):
    return {'cats': Category.objects.all().order_by('name'), 'act_cat': cat, 'pages': Page.objects.all().order_by('title')}
