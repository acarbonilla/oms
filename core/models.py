from django.contrib.auth.models import User
from django.db import models

# Editor for text field
from ckeditor.fields import RichTextField


# Create your models here.

class SBU(models.Model):
    name = models.CharField(max_length=100, verbose_name="Name")
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class StandardImage(models.Model):
    title = models.CharField(max_length=100, verbose_name="Title")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.title}"


class RecentImage(models.Model):
    title = models.CharField(max_length=100, verbose_name="Title")
    remarks = RichTextField(blank=True, null=True)
    re_schedule = models.DateField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated']
        abstract = True

