# Generated by Django 5.0.6 on 2025-03-22 05:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('c2', '0004_c2user_facility'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='c2recentimage',
            name='qr_code',
        ),
    ]
