from django.db import models
from tango_with_django_project import settings


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    likes = models.PositiveIntegerField(default=0)
    views = models.IntegerField(default=0)
    
    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class Page(models.Model):
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title
    
    def __str__(self):
        return self.title
    

