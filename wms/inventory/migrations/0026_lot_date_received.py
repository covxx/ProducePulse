# Generated by Django 4.2.13 on 2024-08-28 14:43

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0025_order_build_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='lot',
            name='date_received',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
